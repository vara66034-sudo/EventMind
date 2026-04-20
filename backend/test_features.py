import os
import sys

# Добавляем путь для корректного импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.api.routes.agent import get_api

def run_tests():
    api = get_api()
    test_user_id = 9999
    
    print("--- 1. Тест сохранения тегов ---")
    response_tags = api.handle_request({
        "action": "update_interests",
        "user_id": test_user_id,
        "interests": ["Python", "Machine Learning", "Hackathon"]
    })
    print(f"Результат: {response_tags}\n")

    print("--- 2. Тест добавления в Избранное ---")
    # Используем фиктивный ID события
    response_add_fav = api.handle_request({
        "action": "add_favorite",
        "user_id": test_user_id,
        "event_id": 42
    })
    print(f"Результат добавления: {response_add_fav}\n")

    print("--- 3. Тест получения списка Избранного ---")
    response_get_fav = api.handle_request({
        "action": "get_favorites",
        "user_id": test_user_id
    })
    print(f"Ваше избранное: {response_get_fav}\n")

    print("--- 4. Тест удаления из Избранного ---")
    response_del_fav = api.handle_request({
        "action": "remove_favorite",
        "user_id": test_user_id,
        "event_id": 42
    })
    print(f"Удаление: {response_del_fav}\n")

    print("--- 5. Повторная проверка Избранного ---")
    response_get_fav2 = api.handle_request({
        "action": "get_favorites",
        "user_id": test_user_id
    })
    print(f"Ваше избранное: {response_get_fav2}\n")

if __name__ == "__main__":
    run_tests()
