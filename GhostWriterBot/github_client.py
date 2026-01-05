"""
GitHub API Client for PR Operations
Handles fetching PR diffs and posting comments using GitHub App authentication.
"""

import requests
from typing import Dict, Optional


class GitHubClient:
    """Client for interacting with GitHub API using installation tokens."""

    def __init__(self, token: str):
        """
        Initialize GitHub client with installation token.

        Args:
            token: GitHub App installation access token
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """
        Fetch the unified diff for a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Unified diff as a string

        Raises:
            Exception: If API request fails
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"

        # Request diff format
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"

        print(f"🔍 Fetching PR diff from: {url}")
        response = requests.get(url, headers=diff_headers)

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch PR diff: {response.status_code} - {response.text}"
            )

        diff_content = response.text
        print(f"✅ Successfully fetched PR diff ({len(diff_content)} characters)")

        return diff_content

    def fetch_pr_metadata(self, owner: str, repo: str, pr_number: int) -> Dict:
        """
        Fetch PR metadata including files changed, additions, deletions.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Dictionary with PR metadata
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"

        print(f"📊 Fetching PR metadata from: {url}")
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch PR metadata: {response.status_code} - {response.text}"
            )

        data = response.json()

        metadata = {
            "title": data.get("title", ""),
            "body": data.get("body", ""),
            "files_changed": data.get("changed_files", 0),
            "additions": data.get("additions", 0),
            "deletions": data.get("deletions", 0),
            "commits": data.get("commits", 0),
        }

        print(
            f"✅ PR Metadata: {metadata['files_changed']} files, "
            f"+{metadata['additions']}/-{metadata['deletions']}"
        )

        return metadata

    def post_pr_comment(
        self, owner: str, repo: str, pr_number: int, comment_body: str
    ) -> bool:
        """
        Post a comment on a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            comment_body: Markdown-formatted comment text

        Returns:
            True if comment posted successfully, False otherwise
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"

        payload = {"body": comment_body}

        print(f"💬 Posting comment to PR #{pr_number}...")
        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code == 201:
            print("✅ Comment successfully posted!")
            return True
        else:
            print(f"❌ Failed to post comment: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    def check_existing_bot_comments(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        bot_identifier: str = "🔍 Automated PR Review Summary",
    ) -> Optional[int]:
        """
        Check if bot has already commented on this PR (for idempotency).

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            bot_identifier: Unique string to identify bot comments

        Returns:
            Comment ID if found, None otherwise
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"⚠️ Could not fetch existing comments: {response.status_code}")
            return None

        comments = response.json()

        for comment in comments:
            if bot_identifier in comment.get("body", ""):
                print(f"ℹ️ Found existing bot comment (ID: {comment['id']})")
                return comment["id"]

        return None

    def update_pr_comment(
        self, owner: str, repo: str, comment_id: int, comment_body: str
    ) -> bool:
        """
        Update an existing PR comment (for idempotency).

        Args:
            owner: Repository owner
            repo: Repository name
            comment_id: ID of the comment to update
            comment_body: New comment body

        Returns:
            True if updated successfully, False otherwise
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/comments/{comment_id}"

        payload = {"body": comment_body}

        print(f"🔄 Updating existing comment (ID: {comment_id})...")
        response = requests.patch(url, headers=self.headers, json=payload)

        if response.status_code == 200:
            print("✅ Comment successfully updated!")
            return True
        else:
            print(f"❌ Failed to update comment: {response.status_code}")
            return False
