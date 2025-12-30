import requests
import json
import sys
import re
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

def get_user_email(headers, owner, repo, pr_number, pr_user_login):
    """
    Fetches the authenticated user's email.
    Priority:
    1. Authenticated User Profile (if token matches PR author)
    2. User Public Profile
    3. Last Commit Author Email in PR (heuristic)
    """
    print(f"[INFO] Attempting to resolve email for user '{pr_user_login}'...")
    
    # 1. Try Authenticated User / Public Profile
    try:
        resp = requests.get("https://api.github.com/user", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            # Verify if the token belongs to the PR author or we are just acting as them
            if data.get("login") == pr_user_login: 
                if data.get("email"):
                    return data["email"]
                
                # Try emails endpoint
                resp_emails = requests.get("https://api.github.com/user/emails", headers=headers)
                if resp_emails.status_code == 200:
                    emails = resp_emails.json()
                    for email in emails:
                        if email.get("primary") and email.get("verified"):
                            return email["email"]
    except Exception as e:
        print(f"[warning] Profile email fetch failed: {e}")

    # 2. Try Commit History (Heuristic)
    try:
        print("[INFO] Profile email not found. Checking PR commit history...")
        commits_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        resp = requests.get(commits_url, headers=headers)
        if resp.status_code == 200:
            commits = resp.json()
            # Look for a commit by this user (reverse order to get latest)
            for commit in reversed(commits): 
                author = commit.get("author") or {}
                commit_info = commit.get("commit", {}).get("author", {})
                
                # Match by login if possible, or key off the fact they are the PR author
                if author.get("login") == pr_user_login:
                    email = commit_info.get("email")
                    if email and "noreply" not in email:
                        return email
                    
    except Exception as e:
        print(f"[warning] Commit email fetch failed: {e}")

    return None

def fetch_real_pr(pr_url, provided_email=None):
    # Target the Node.js Backend (The Fetcher)
    webhook_url = "http://localhost:3001/api/webhook/github"
    
    # Parse URL 
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        print("❌ Error: Invalid GitHub PR URL format.")
        print("Expected: https://github.com/owner/repo/pull/number")
        return

    owner = match.group(1)
    repo_name = match.group(2)
    pr_number = int(match.group(3))
    
    print(f"[INFO] Analyzing PR: {owner}/{repo_name} #{pr_number}")
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        gh_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}"
        print(f"[INFO] Fetching PR metadata from GitHub API: {gh_api_url}...")
        gh_response = requests.get(gh_api_url, headers=headers)
        
        if gh_response.status_code != 200:
            print(f"[ERROR] Failed to fetch PR details from GitHub: {gh_response.status_code}")
            return
            
        pr_data = gh_response.json()
        pr_user_login = pr_data["user"]["login"]

        # Determind User Email
        user_email = provided_email
        
        if user_email:
            print(f"[INFO] Using provided logged-in user email: {user_email}")
        else:
            # Fallback to auto-detection
            user_email = get_user_email(headers, owner, repo_name, pr_number, pr_user_login)
            if user_email:
                print(f"[INFO] Identified Target Email (Auto-detected): {user_email}")
            else:
                print("[INFO] Could not resolve email. Audit will not be emailed.")

        # Construct Payload
        payload = {
            "action": "opened",
            "pull_request": {
                "number": pr_number,
                "title": pr_data.get("title", f"PR #{pr_number}"),
                "body": pr_data.get("body", "No description provided"),
                "html_url": pr_data.get("html_url", pr_url),
                "diff_url": pr_data.get("diff_url", "")
            },
            "repository": {
                "name": repo_name,
                "owner": {"login": owner},
                "full_name": f"{owner}/{repo_name}"
            },
            "email": user_email
        }
        
        print(f"[INFO] Triggering Node.js Backend...")
        headers = {"X-GitHub-Event": "pull_request"}
        response = requests.post(webhook_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("\n[SUCCESS] The backend accepted the request.")
            print("[DEBUG] Raw Response:", response.text)
            print("[DEBUG] Backend Response:", response.json())
        else:
            print(f"\n[ERROR] Failed. Backend responded with: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch PR data and trigger analysis")
    parser.add_argument("url", help="GitHub PR URL")
    parser.add_argument("--email", help="Explicit email of the user to notify", default=None)
    
    args = parser.parse_args()
    
    fetch_real_pr(args.url, args.email)
