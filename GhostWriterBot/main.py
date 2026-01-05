"""
DevOps-GhostWriter - Production-Grade Multi-Agent PR Reviewer
GitHub App webhook bot that automatically reviews PRs using three agents:
- Security Auditor: Scans for security vulnerabilities
- Runtime Validator: Detects runtime logic flaws
- Ghostwriter: Synthesizes findings into professional PR comments
"""

import hmac
import hashlib
import json
import time
import jwt
import os
import asyncio
from typing import Optional

from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from dotenv import load_dotenv

# Import our service modules
from github_client import GitHubClient
from agent_service import create_orchestrator

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------
load_dotenv()

GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

# Load private key
try:
    with open("private-key.pem", "r") as f:
        GITHUB_PRIVATE_KEY = f.read()
except FileNotFoundError:
    print("❌ ERROR: private-key.pem not found!")
    print("Please ensure the GitHub App private key is in the same directory.")
    raise

app = FastAPI(
    title="DevOps-GhostWriter",
    description="Multi-Agent PR Review System",
    version="1.0.0",
)


# --------------------------------------------------
# Verify GitHub Webhook Signature
# --------------------------------------------------
def verify_signature(payload: bytes, signature: str) -> None:
    """
    Verify GitHub webhook signature for security.

    Args:
        payload: Raw webhook payload
        signature: X-Hub-Signature-256 header value

    Raises:
        HTTPException: If signature is missing or invalid
    """
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


# --------------------------------------------------
# Create GitHub App JWT
# --------------------------------------------------
def create_jwt() -> str:
    """
    Create a JWT for GitHub App authentication.

    Returns:
        Encoded JWT token
    """
    payload = {
        "iat": int(time.time()) - 60,  # Issued at (60s in past for clock skew)
        "exp": int(time.time()) + 600,  # Expires in 10 minutes
        "iss": GITHUB_APP_ID,
    }

    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")


# --------------------------------------------------
# Get Installation Access Token
# --------------------------------------------------
def get_installation_token(installation_id: int) -> str:
    """
    Get an installation access token for the GitHub App.

    Args:
        installation_id: GitHub App installation ID

    Returns:
        Installation access token

    Raises:
        Exception: If token request fails
    """
    jwt_token = create_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    import requests

    response = requests.post(url, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Failed to get installation token: {response.text}")

    return response.json()["token"]


# --------------------------------------------------
# Background Task: Process PR Review
# --------------------------------------------------
async def process_pr_review(
    installation_id: int, repo_full_name: str, pr_number: int, action: str
) -> None:
    """
    Background task to process PR review with multi-agent system.
    This runs asynchronously to avoid blocking the webhook response.

    Args:
        installation_id: GitHub App installation ID
        repo_full_name: Full repository name (owner/repo)
        pr_number: Pull request number
        action: PR action (opened, synchronize)
    """
    try:
        print("\n" + "=" * 70)
        print(f"🚀 PROCESSING PR REVIEW (Background Task)")
        print("=" * 70)
        print(f"Repository: {repo_full_name}")
        print(f"PR Number: {pr_number}")
        print(f"Action: {action}")

        # Step 1: Get installation token
        print("\n🔑 Obtaining GitHub App installation token...")
        token = get_installation_token(installation_id)
        print("✅ Token obtained")

        # Step 2: Initialize GitHub client
        github_client = GitHubClient(token)

        # Parse owner and repo
        owner, repo = repo_full_name.split("/")

        # Step 3: Fetch PR diff
        print("\n📥 STEP 1: Fetching PR diff...")
        pr_diff = github_client.fetch_pr_diff(owner, repo, pr_number)

        # Step 4: Fetch PR metadata
        pr_metadata = github_client.fetch_pr_metadata(owner, repo, pr_number)

        # Step 5: Check for existing bot comment (idempotency)
        existing_comment_id = github_client.check_existing_bot_comments(
            owner, repo, pr_number
        )

        # Step 6: Run multi-agent orchestration
        orchestrator = await create_orchestrator()

        final_comment = await orchestrator.orchestrate_pr_review(
            pr_diff=pr_diff, pr_metadata=pr_metadata, pr_number=pr_number
        )

        # Step 7: Post or update PR comment
        print("\n💬 STEP 5: Posting PR comment...")

        if existing_comment_id:
            # Update existing comment for idempotency
            success = github_client.update_pr_comment(
                owner, repo, existing_comment_id, final_comment
            )
        else:
            # Post new comment
            success = github_client.post_pr_comment(
                owner, repo, pr_number, final_comment
            )

        if success:
            print("\n" + "=" * 70)
            print("🎉 PR REVIEW COMPLETE - Comment posted successfully!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("⚠️ PR REVIEW COMPLETE - But failed to post comment")
            print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR in background PR review task: {e}")
        print("=" * 70)
        import traceback

        traceback.print_exc()


# --------------------------------------------------
# GitHub Webhook Endpoint
# --------------------------------------------------
@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None),
):
    """
    Main webhook endpoint for GitHub events.
    Handles pull_request.opened and pull_request.synchronize events.

    Returns HTTP 200 immediately and processes review in background.
    """
    # Verify webhook signature
    payload = await request.body()
    verify_signature(payload, x_hub_signature_256)

    data = json.loads(payload)

    print("\n📩 Webhook received")
    print(f"➡ Event Type: {x_github_event}")

    # Only process pull_request events
    if x_github_event != "pull_request":
        print(f"ℹ️ Ignoring non-PR event: {x_github_event}")
        return {"status": "ignored", "reason": "not a pull_request event"}

    action = data.get("action")
    print(f"➡ PR Action: {action}")

    # Only handle 'opened' and 'synchronize' actions
    if action not in ["opened", "synchronize"]:
        print(f"ℹ️ Ignoring PR action: {action}")
        return {"status": "ignored", "reason": f"action '{action}' not handled"}

    # Extract PR information
    installation_id = data["installation"]["id"]
    repo_full_name = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]

    print(f"✅ Valid PR event detected!")
    print(f"📦 Repository: {repo_full_name}")
    print(f"🔢 PR Number: {pr_number}")

    # Add background task to process PR review
    # This allows us to return HTTP 200 immediately
    background_tasks.add_task(
        process_pr_review,
        installation_id=installation_id,
        repo_full_name=repo_full_name,
        pr_number=pr_number,
        action=action,
    )

    print("⏳ PR review queued for background processing")
    print("🚀 Returning HTTP 200 to GitHub")

    return {
        "status": "queued",
        "pr_number": pr_number,
        "repository": repo_full_name,
        "action": action,
    }


# --------------------------------------------------
# Health Check Endpoint
# --------------------------------------------------
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "DevOps-GhostWriter", "version": "1.0.0"}


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "DevOps-GhostWriter",
        "description": "Multi-Agent PR Review System",
        "version": "1.0.0",
        "agents": ["Security Auditor", "Runtime Validator", "Ghostwriter"],
        "endpoints": {"webhook": "/webhook/github", "health": "/health"},
    }


# --------------------------------------------------
# Startup Event
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Print startup information."""
    print("\n" + "=" * 70)
    print("🤖 DevOps-GhostWriter - Multi-Agent PR Review System")
    print("=" * 70)
    print("✅ Service started successfully")
    print(f"📋 GitHub App ID: {GITHUB_APP_ID}")
    print("🔐 Webhook signature verification: ENABLED")
    print("🤖 Agents loaded:")
    print("   - Security Auditor Agent")
    print("   - Runtime Validator Agent")
    print("   - Ghostwriter Agent")
    print("=" * 70)
    print("🎯 Ready to review pull requests!")
    print("=" * 70 + "\n")
