import os
from google import genai
from dotenv import load_dotenv

load_dotenv('../.env.local')

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env.local")
    exit(1)

client = genai.Client(api_key=api_key)

print(f"Checking models with key: {api_key[:5]}...")

try:
    # List models
    # Note: The exact method to list models in the new SDK might differ slightly, 
    # but let's try the common iterate method or similar.
    # If client.models.list() exists:
    count = 0
    print("Available Models:")
    for model in client.models.list():
        print(f"- {model.name}")
        count += 1
    
    if count == 0:
        print("No models found. Check API Key permissions.")

except Exception as e:
    print(f"Error listing models: {e}")

# Try a simple generation with a known safe model name
try:
    print("\nTesting generation with 'gemini-2.5-flash'...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello"
    )
    print("Success! Response:", response.text)
except Exception as e:
    print(f"Failed to generate with 'gemini-2.5-flash': {e}")
