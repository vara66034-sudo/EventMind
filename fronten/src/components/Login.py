#!/usr/bin/env python3
import os
import sys
import getpass
import requests

# URL бэкенда (можно задать через переменную окружения)
API_URL = os.getenv("VITE_API_URL", "http://localhost:8000/api")

def login(email: str, password: str) -> dict:
    """Отправляет запрос на вход"""
    payload = {"action": "login", "email": email, "password": password}
    try:
        resp = requests.post(f"{API_URL}/auth", json=payload)
        return resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=== EventMind Login ===\n")
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")
    print("\nLogging in...")

    result = login(email, password)

    if result.get("success"):
        user = result["data"]
        print(f" Welcome, {user.get('name', user.get('email'))}!")
        print(f"User ID: {user.get('user_id')}")
    else:
        print(f" Login failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
