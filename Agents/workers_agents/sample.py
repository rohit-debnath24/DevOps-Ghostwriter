import os
import time
import sqlite3
import pickle

API_KEY = ""

DB_PASSWORD = "admin123"

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
