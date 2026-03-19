#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тесты для ics_generator.py"""

import sys
from pathlib import Path

# Добавляем папку с модулем в путь импорта
sys.path.insert(0, str(Path(__file__).parent / 'eventmind_notify'))

from ics_generator import ICSGenerator, get_ics_generator, reset_ics_generator


def test_basic_ics_generation():
    """Тест 1: Базовая генерация .ics"""
    print("\n Тест 1: Базовая генерация .ics")
    
    reset_ics_generator()
    gen = get_ics_generator()
    
    event = {
        'id': 123,
        'name': 'Test Event',
        'date_begin': '2024-12-25T18:00:00+03:00',
        'date_end': '2024-12-25T20:00:00+03:00',
        'location': 'Moscow, Office',
        'description': 'Test with special chars: < > & " ; , \n'
    }
    
    ics = gen.generate_ics(event)
    
    # Проверки
    assert 'BEGIN:VCALENDAR' in ics, "Missing VCALENDAR header"
    assert 'VERSION:2.0' in ics, "Missing VERSION"
    assert 'SUMMARY:Test Event' in ics, "Missing event name"
    assert 'DTSTART:20241225T180000Z' in ics, "Wrong date format"
    assert 'LOCATION:Moscow\\, Office' in ics, "Location not escaped"
    assert 'DESCRIPTION:Test with special chars:' in ics, "Description missing"
    
    print("Все проверки пройдены")
    print(f"Сгенерировано {len(ics)} символов")
    return True


def test_escaping():
    """Тест 2: Экранирование специальных символов"""
    print("\n Тест 2: Экранирование текста")
    
    gen = ICSGenerator()
    
    test_cases = [
        ('simple text', 'simple text'),
        ('text, with comma', 'text\\, with comma'),
        ('text; with semicolon', 'text\\; with semicolon'),
        ('text\nwith newline', 'text\\nwith newline'),
        ('text\\with backslash', 'text\\\\with backslash'),
        ('', ''),
        (None, ''),
    ]
    
    for input_text, expected in test_cases:
        result = gen._escape_ics_text(input_text)
        assert result == expected, f"Failed: '{input_text}' → '{result}' != '{expected}'"
        print(f"  ✓ '{input_text}' → '{result}'")
    
    print("Все символы экранируются правильно")
    return True


def test_datetime_formatting():
    """Тест 3: Форматирование дат"""
    print("\n Тест 3: Форматирование дат")
    
    gen = ICSGenerator()
    
    # Тест строки с timezone
    result1 = gen._format_datetime('2024-12-25T18:00:00+03:00')
    assert result1 == '20241225T180000Z', f"Wrong format: {result1}"
    print(f"  ✓ ISO string → {result1}")
    
    # Тест datetime объекта
    from datetime import datetime
    dt = datetime(2024, 12, 25, 18, 0, 0)
    result2 = gen._format_datetime(dt)
    assert result2 == '20241225T180000Z', f"Wrong format: {result2}"
    print(f"  ✓ datetime object → {result2}")
    
    print("Даты форматируются в UTC с суффиксом Z")
    return True


def test_api_response():
    """Тест 4: API-метод возвращает правильную структуру"""
    print("\n Тест 4: API-ответ")
    
    gen = ICSGenerator()
    event = {
        'id': 456,
        'name': 'API Test',
        'date_begin': '2024-06-01T12:00:00Z'
    }
    
    result = gen.api_generate_ics(event)
    
    assert result['success'] is True, "success should be True"
    assert 'data' in result, "Missing 'data' key"
    assert 'content' in result['data'], "Missing 'content' in data"
    assert result['code'] == 200, f"Wrong code: {result['code']}"
    assert result['data']['filename'] == 'event_456.ics', "Wrong filename"
    
    print(f"API-ответ структурирован правильно")
    print(f"   Код: {result['code']}, Файл: {result['data']['filename']}")
    return True


def test_validation():
    """Тест 5: Валидация .ics контента"""
    print("\n Тест 5: Валидация ICS")
    
    gen = ICSGenerator()
    
    # Валидный контент
    valid_ics = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
END:VEVENT
END:VCALENDAR"""
    assert gen.validate_ics(valid_ics) is True, "Valid ICS should pass"
    print("  ✓ Валидный .ics распознан")
    
    # Невалидный контент
    invalid_ics = "BEGIN:VCALENDAR\nEND:VCALENDAR"  # нет VEVENT
    assert gen.validate_ics(invalid_ics) is False, "Invalid ICS should fail"
    print("  ✓ Невалидный .ics отклонён")
    
    # Тест через API
    api_result = gen.api_validate_ics(valid_ics)
    assert api_result['data']['valid'] is True
    print("  ✓ API-валидация работает")
    
    print("Валидация работает корректно")
    return True


def run_all_tests():
    """Запустить все тесты"""
    print("Запуск тестов для ics_generator.py")
    print("=" * 50)
    
    tests = [
        test_basic_ics_generation,
        test_escaping,
        test_datetime_formatting,
        test_api_response,
        test_validation,
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
    
    print("\n" + "=" * 50)
    print(f"Результат: {passed}/{len(tests)} тестов пройдено")
    
    if passed == len(tests):
        print("Все тесты ics_generator.py пройдены!")
        return True
    else:
        print("Некоторые тесты не прошли")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
