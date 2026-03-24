import os
import requests
from typing import Dict, Optional

# Конфигурация – URL бэкенда
API_URL = os.getenv("VITE_API_URL", "http://localhost:8000/api")

# Глобальное хранилище (имитация localStorage)
_token = None
_user = None

class AuthAPI:
    @staticmethod
    def register(email: str, password: str, name: str = None) -> Dict:
        """Регистрация пользователя"""
        payload = {
            "action": "register",
            "email": email,
            "password": password,
            "name": name
        }
        response = requests.post(f"{API_URL}/auth", json=payload)
        return response.json()

    @staticmethod
    def login(email: str, password: str) -> Dict:
        """Вход пользователя"""
        payload = {
            "action": "login",
            "email": email,
            "password": password
        }
        response = requests.post(f"{API_URL}/auth", json=payload)
        data = response.json()
        if data.get("success"):
            global _token, _user
            _token = data["data"].get("token")
            _user = data["data"]
        return data

    @staticmethod
    def logout() -> Dict:
        """Выход пользователя"""
        global _token, _user
        if _token:
            payload = {"action": "logout", "token": _token}
            requests.post(f"{API_URL}/auth", json=payload)
        _token = None
        _user = None
        return {"success": True}

    @staticmethod
    def get_current_user() -> Optional[Dict]:
        """Возвращает данные текущего пользователя"""
        return _user

    @staticmethod
    def is_authenticated() -> bool:
        """Проверка авторизации"""
        return _token is not None

    @staticmethod
    def get_token() -> Optional[str]:
        """Возвращает текущий токен"""
        return _token
