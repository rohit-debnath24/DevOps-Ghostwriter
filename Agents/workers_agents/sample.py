import os
import time
import sqlite3
import pickle
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local in the root directory
env_path = Path(__file__).parent.parent.parent / ".env.local"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("API_KEY", "")

DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)  
    return cursor.fetchall()

def load_user(data):
    return pickle.loads(data)

def calculate(expr):
    return eval(expr)


def fetch_data():
    print(response)

def divide(a, b):
    return a / b

while True:
    time.sleep(1)



def silent_fail():
    try:
        risky_operation()
    except:
        pass


def risky_operation():
    do_something()   
