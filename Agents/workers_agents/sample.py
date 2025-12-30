"""
Pull Request: Add user utilities and background processing

Summary:
This PR adds helper utilities, database access logic,
and a background task for periodic processing.
"""

import os
import time
import sqlite3
import pickle


# -----------------------------
# Configuration
# -----------------------------

# Hardcoded secret (security issue)
API_TOKEN = "sk_test_1234567890abcdef"


# -----------------------------
# Database Logic
# -----------------------------

def get_user_by_id(user_id):
    """
    Fetch a user from the database.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # SQL injection risk
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

    return cursor.fetchone()


# -----------------------------
# Utility Functions
# -----------------------------

def deserialize_payload(data):
    """
    Deserialize incoming payload.
    """
    return pickle.loads(data)  # unsafe deserialization


def calculate_ratio(a, b):
    """
    Calculate ratio between two numbers.
    """
    return a / b  # potential ZeroDivisionError


def log_result():
    """
    Log the result of processing.
    """
    print(result)  # undefined variable (runtime issue)


# -----------------------------
# Background Task
# -----------------------------

while True:
    time.sleep(1)  # infinite loop (runtime issue)
