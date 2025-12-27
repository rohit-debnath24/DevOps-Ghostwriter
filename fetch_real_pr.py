import requests
import json
import sys
import re

def fetch_real_pr(pr_url):
    # Target the Node.js Backend (The Fetcher)
    webhook_url = "http://localhost:3001/api/webhook/github"
    
    # Parse URL 
    # expected format: https://github.com/OWNER/REPO/pull/NUMBER
    match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if not match:
        print("❌ Error: Invalid GitHub PR URL format.")
        print("Expected: https://github.com/owner/repo/pull/number")
        return

    owner = match.group(1)
    repo_name = match.group(2)
    pr_number = int(match.group(3))
    
    print(f"[INFO] Analyzing PR: {owner}/{repo_name} #{pr_number}")
    
    # Fetch real PR details from GitHub API (Public)
    try:
        gh_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pr_number}"
        print(f"[INFO] Fetching PR metadata from GitHub API: {gh_api_url}...")
        gh_response = requests.get(gh_api_url)
        
        if gh_response.status_code != 200:
            print(f"[ERROR] Failed to fetch PR details from GitHub: {gh_response.status_code}")
            print(gh_response.text)
            return
            
        pr_data = gh_response.json()
        
        # Construct Payload matching a real GitHub Webhook structure
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
                "owner": {
                    "login": owner
                },
                "full_name": f"{owner}/{repo_name}"
            }
        }
        
        headers = {
            "X-GitHub-Event": "pull_request"
        }
    
        print(f"[INFO] Triggering Node.js Backend with real data...")
        
        response = requests.post(webhook_url, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\n[SUCCESS] The backend accepted the request.")
            print("Check your 'backend' terminal (npm start) to see the processing logs.")
        else:
            print(f"\n[ERROR] Failed. Backend responded with: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {e}")

if __name__ == "__main__":
    print(f"DEBUG: sys.argv: {sys.argv}")
    if len(sys.argv) < 2:
        print("Usage: python fetch_real_pr.py <github_pr_url>")
        sys.exit(1)
    else:
        fetch_real_pr(sys.argv[1])
