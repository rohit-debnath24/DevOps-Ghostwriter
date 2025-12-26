import requests
import json
import time

def test_python_agent():
    print("Testing Python Agent Engine...")
    url = "http://localhost:8000/analyze"
    payload = {
        "repo_id": "test/repo",
        "pr_id": 123,
        "diff_text": """diff --git a/server.js b/server.js
index 823..234 100644
--- a/server.js
+++ b/server.js
@@ -10,1 +10,1 @@
- const password = process.env.PASSWORD;
+ const password = 'hardcoded_secret_123';""",
        "title": "Test PR",
        "description": "Adding a secret"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Body:", response.text)
    except Exception as e:
        print(f"Failed to connect to Python Agent: {e}")

def test_node_backend():
    print("\nTesting Node.js Backend (Webhook)...")
    url = "http://localhost:3001/api/webhook/github"
    # This payload mocks a GitHub Pull Request event
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 1,
            "title": "Test PR",
            "body": "Testing Webhook"
        },
        "repository": {
            "name": "test_repo",
            "owner": {
                "login": "test_owner"
            },
            "full_name": "test_owner/test_repo"
        }
    }
    headers = {
        "X-GitHub-Event": "pull_request"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)
    except Exception as e:
        print(f"Failed to connect to Node.js Backend: {e}")

if __name__ == "__main__":
    test_python_agent()
    test_node_backend()
