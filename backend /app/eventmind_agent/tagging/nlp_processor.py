import re
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """
    Очищает текст события:
    - приводит к нижнему регистру
    - удаляет ссылки
    - удаляет спецсимволы
    - нормализует пробелы
    """

    if not text:
        return ""

    text = text.lower()

    # удаляем ссылки
    text = re.sub(r"http\S+", "", text)

    # удаляем спецсимволы (оставляем буквы и цифры)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # убираем лишние пробелы
    text = re.sub(r"\s+", " ", text).strip()

    return text
