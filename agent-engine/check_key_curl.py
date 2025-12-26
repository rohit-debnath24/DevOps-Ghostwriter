import os
import requests
from dotenv import load_dotenv

load_dotenv('../.env.local')
key = os.getenv("GEMINI_API_KEY")

if not key:
    print("No key found!")
    exit(1)

print(f"Testing key ending in ...{key[-4:]}")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
try:
    response = requests.get(url)
    print("Status:", response.status_code)
    print("Response:", response.text) # Print ALL text
except Exception as e:
    print(f"Error: {e}")
