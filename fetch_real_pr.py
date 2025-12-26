import requests
import json

def fetch_real_pr():
    # Target the Node.js Backend (The Fetcher)
    url = "http://localhost:3001/api/webhook/github"
    
    # Payload matching a real GitHub Webhook structure
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 2,
            "title": "Real PR Test",
            "body": "Testing fetching from real repo"
        },
        "repository": {
            "name": "Articuno.AI",
            "owner": {
                "login": "BikramMondal5"
            },
            "full_name": "BikramMondal5/Articuno.AI"
        }
    }
    
    headers = {
        "X-GitHub-Event": "pull_request"
    }

    print(f"Triggering Node.js Backend to fetch PR #2 from BikramMondal5/Articuno.AI...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Success! The backend accepted the request.")
            print("Check your 'backend' terminal (npm start) to see if it says:")
            print("   'Fetched diff (length: ...)'")
        else:
            print("\n❌ Failed. Check backend logs.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_real_pr()
