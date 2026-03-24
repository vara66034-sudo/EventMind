#!/usr/bin/env python3
"""
Консольный скрипт регистрации пользователя (аналог React‑компонента Register)
"""

import os
import sys
import getpass
import requests

# URL бэкенда (по умолчанию локальный, можно переопределить через переменную окружения)
API_URL = os.getenv("VITE_API_URL", "http://localhost:8000/api")


def register(email: str, password: str, name: str = None) -> dict:
    """Отправляет запрос на регистрацию"""
    payload = {"action": "register", "email": email, "password": password}
    if name:
        payload["name"] = name
    try:
        resp = requests.post(f"{API_URL}/auth", json=payload)
        return resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=== EventMind Registration ===\n")

    name = input("Имя (опционально): ").strip() or None
    email = input("Email: ").strip()
    password = getpass.getpass("Пароль: ")
    confirm = getpass.getpass("Подтвердите пароль: ")

    if password != confirm:
        print("Пароли не совпадают")
        sys.exit(1)
    if len(password) < 6:
        print("Пароль должен быть не менее 6 символов")
        sys.exit(1)

    print("\nРегистрация...")
    result = register(email, password, name)

    if not result.get("success"):
        print(f"Ошибка регистрации: {result.get('error', 'Неизвестная ошибка')}")
        sys.exit(1)

    # Автоматический вход после регистрации
    login_payload = {"action": "login", "email": email, "password": password}
    try:
        login_resp = requests.post(f"{API_URL}/auth", json=login_payload)
        login_data = login_resp.json()
        if login_data.get("success"):
            user = login_data["data"]
            print(f"\nРегистрация и вход выполнены! Добро пожаловать, {user.get('name', email)}!")
            with open(".token", "w") as f:
                f.write(user.get("token", ""))
            with open(".user.json", "w") as f:
                import json
                json.dump(user, f)
        else:
            print("\n Регистрация прошла, но автоматический вход не удался. Попробуйте войти вручную.")
    except Exception as e:
        print(f"\n Регистрация прошла, но ошибка при входе: {e}")


if __name__ == "__main__":
    main()
