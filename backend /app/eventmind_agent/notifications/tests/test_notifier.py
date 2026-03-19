#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тесты для notifier.py"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Настройка путей и окружения
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / 'eventmind_notify'))

# Переменные окружения для тестов
os.environ['SMTP_SERVER'] = 'localhost'
os.environ['SMTP_PORT'] = '1025'
os.environ['EMAIL_FROM'] = 'test@eventmind.local'
os.environ['BASE_URL'] = 'http://localhost:8069'

from notifier import Notifier, get_notifier, reset_notifier


def test_notifier_init():
    """Тест 1: Инициализация Notifier"""
    print("\n Тест 1: Инициализация Notifier")
    
    reset_notifier()
    
    config_path = BASE_DIR / 'test_config.json'
    notifier = get_notifier(config_path=str(config_path))
    
    assert notifier is not None, "Notifier not created"
    assert notifier.config['smtp']['server'] == 'localhost', "Config not loaded"
    assert notifier.base_url == 'http://localhost:8069', "Base URL not set"
    
    print("Notifier инициализирован корректно")
    return True


def test_text_escaping():
    """Тест 2: Экранирование текста для HTML"""
    print("\n Тест 2: Экранирование текста")
    
    notifier = Notifier()
    
    test_cases = [
        ('<script>', '&lt;script&gt;'),
        ('Tom & Jerry', 'Tom &amp; Jerry'),
        ('Quote "test"', 'Quote &quot;test&quot;'),
        ('', ''),
    ]
    
    for input_text, expected in test_cases:
        result = notifier._escape_text(input_text)
        assert result == expected, f"'{input_text}' → '{result}' != '{expected}'"
        print(f"  ✓ '{input_text}' → '{result}'")
    
    print("Текст экранируется для HTML")
    return True


def test_url_building():
    """Тест 3: Построение абсолютных URL"""
    print("\n Тест 3: Построение URL")
    
    notifier = Notifier(base_url='https://myapp.com')
    
    tests = [
        ('/event/123/ics', 'https://myapp.com/event/123/ics'),
        ('event/456/ics', 'https://myapp.com/event/456/ics'),
        ('https://external.com/link', 'https://external.com/link'),  # уже абсолютный
    ]
    
    for relative, expected in tests:
        result = notifier._build_absolute_url(relative)
        assert result == expected, f"'{relative}' → '{result}' != '{expected}'"
        print(f"  ✓ '{relative}' → '{result}'")
    
    print("Абсолютные URL строятся корректно")
    return True


def test_reminder_logic():
    """Тест 4: Логика расчёта времени до события"""
    print("\n Тест 4: Логика напоминаний")
    
    notifier = Notifier()
    
    # Тест: событие через 26 часов → "1 day"
    future = (datetime.now() + timedelta(hours=26)).isoformat()
    event = {
        'id': 1,
        'name': 'Future Event',
        'date_begin': future,
    }
    
    # Проверяем, что метод не падает (полная отправка требует SMTP)
    result = notifier.send_reminder(
        user_email='test@example.com',
        user_name='Test User',
        event=event,
        hours_before=24
    )
    
    # В тестовой среде с localhost:1025 должно сработать
    # Если SMTP не запущен — будет False, но без исключения
    print(f"  ✓ send_reminder вернул: {result}")
    print("Логика напоминаний не вызывает ошибок")
    return True


def test_batch_reminders():
    """Тест 5: Пакетная отправка"""
    print("\n Тест 5: Пакетная отправка")
    
    notifier = Notifier()
    
    reminders = [
        {
            'user_email': 'user1@example.com',
            'user_name': 'User One',
            'event': {
                'id': 1,
                'name': 'Event 1',
                'date_begin': (datetime.now() + timedelta(hours=25)).isoformat(),
            },
        },
        {
            'user_email': 'user2@example.com',
            'user_name': 'User Two',
            'event': {
                'id': 2,
                'name': 'Event 2',
                'date_begin': (datetime.now() + timedelta(hours=26)).isoformat(),
            },
        },
    ]
    
    result = notifier.send_batch_reminders(reminders)
    
    assert 'total' in result, "Missing 'total' in result"
    assert 'successful' in result, "Missing 'successful' in result"
    assert 'failed' in result, "Missing 'failed' in result"
    assert result['total'] == 2, f"Wrong total: {result['total']}"
    
    print(f"  ✓ Пакет: {result['successful']} успешно, {result['failed']} ошибок")
    print("Пакетная отправка работает")
    return True


def test_api_methods():
    """Тест 6: API-методы возвращают правильную структуру"""
    print("\n Тест 6: API-методы")
    
    notifier = Notifier()
    
    # Тест api_get_stats
    stats = notifier.api_get_stats()
    assert stats['success'] is True
    assert 'data' in stats
    assert 'total_sent' in stats['data']
    print("  ✓ api_get_stats возвращает правильную структуру")
    
    # Тест api_test_connection (может упасть, если SMTP не запущен)
    conn = notifier.api_test_connection()
    assert 'success' in conn
    assert 'code' in conn
    print(f"  ✓ api_test_connection: код {conn['code']}")
    
    # Тест api_send_reminder с валидными данными
    payload = {
        'user_email': 'api@test.com',
        'user_name': 'API User',
        'event': {
            'id': 999,
            'name': 'API Event',
            'date_begin': (datetime.now() + timedelta(hours=25)).isoformat(),
        }
    }
    send_result = notifier.api_send_reminder(payload)
    assert 'success' in send_result
    assert 'code' in send_result
    print(f"  ✓ api_send_reminder: код {send_result['code']}")
    
    # Тест api_send_reminder с НЕвалидными данными
    bad_payload = {'user_email': 'test@test.com'}  # нет user_name и event
    bad_result = notifier.api_send_reminder(bad_payload)
    assert bad_result['success'] is False
    assert bad_result['code'] == 400
    print(f"  ✓ api_send_reminder (ошибка): код {bad_result['code']}")
    
    print("API-методы возвращают структурированные ответы")
    return True


def test_ics_integration():
    """Тест 7: Интеграция с ICSGenerator"""
    print("\n Тест 7: Интеграция с ICS")
    
    notifier = Notifier()
    
    event = {
        'id': 777,
        'name': 'ICS Test Event',
        'date_begin': '2024-12-25T18:00:00Z',
        'location': 'Test Location',
    }
    
    # Тест через api_get_ics
    ics_result = notifier.api_get_ics(event)
    assert ics_result['success'] is True
    assert 'content' in ics_result['data']
    assert 'BEGIN:VCALENDAR' in ics_result['data']['content']
    assert ics_result['data']['filename'] == 'event_777.ics'
    
    print(f"  ✓ ICS сгенерирован: {len(ics_result['data']['content'])} символов")
    print("Интеграция с ICSGenerator работает")
    return True


def run_all_tests():
    """Запустить все тесты notifier"""
    print("Запуск тестов для notifier.py")
    print("=" * 50)
    print("Убедись, что запущен SMTP-сервер: python -m smtpd -c DebuggingServer -n localhost:1025")
    print()
    
    tests = [
        test_notifier_init,
        test_text_escaping,
        test_url_building,
        test_reminder_logic,
        test_batch_reminders,
        test_api_methods,
        test_ics_integration,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"Результат: {passed}/{len(tests)} тестов пройдено")
    
    if passed == len(tests):
        print("Все тесты notifier.py пройдены!")
        return True
    else:
        print("Некоторые тесты не прошли")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
