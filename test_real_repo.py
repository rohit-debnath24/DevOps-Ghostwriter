import requests
import json

def test_real_repo():
    url = "http://localhost:8000/analyze"
    
    # This matches the payload you were trying to send via curl
    payload = {
        "repo_id": "https://github.com/rohit-debnath24/Spylt",
        "pr_id": 1, 
        "diff_text": "print(\"hello from manual test\")",
        "title": "Manual Test PR",
        "description": "Testing with specific repo URL"
    }

    print(f"Sending request to {url}...")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, json=payload)
        print("\n--- Response ---")
        print(f"Status: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    test_real_repo()
