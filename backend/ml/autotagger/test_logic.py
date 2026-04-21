from tagging.pipeline import TaggingPipeline


def test_manual():
    pipeline = TaggingPipeline()

    # Тестовое событие
    mock_event = {
        "title": "Фестиваль джазовых Концертов",
        "description": "Приходите на наши концерты в Москве! Ссылка: http://jazz.ru"
    }

    print("--- Запуск теста ---")
    result = pipeline.process_event(mock_event)

    print(f"Очищенный текст: {result['text']}")
    print(f"Сгенерированные теги: {result['tags']}")
    print(f"Длина эмбеддинга: {len(result['embedding'])}")

    # Проверка лемматизации: ищем корень "концерт" в любом из тегов
    found_lemma = any("концерт" in tag for tag in result['tags'])
    found_plural = any("концерты" in tag for tag in result['tags'])

    if found_lemma and not found_plural:
        print("✅ Успех: Лемматизация работает корректно!")
    else:
        print("❌ Ошибка: В тегах до сих пор множественное число или слова не найдены.")


if __name__ == "__main__":
    test_manual()
