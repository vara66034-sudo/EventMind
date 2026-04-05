import json
import psycopg2
import html
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

TIMEPAD_API_URL = "https://api.timepad.ru/v1/events.json"
TIMEPAD_TOKEN = "fbf148c84bdcf452d12fc82054cffdacd7a26479"

CITY = "Екатеринбург"
LIMIT = 100
DAYS_AHEAD = 365

ORGANIZATION_IDS: List[int] = []

# Сильные IT-маркеры: если найден хотя бы один — событие почти точно IT
STRONG_IT = [
    "разработк", "developer", "разработчик", "разработчиков",
    "frontend", "backend", "fullstack",
    "mobile development", "мобильная разработка",
    "python", "java", "javascript", "typescript", "sql",
    "c++", "c#", "golang", "go", "php",
    "data science", "data analyst", "data analytics",
    "аналитика данных", "аналитик данных",
    "machine learning", "ml", "ai", "genai",
    "devops", "qa", "test automation",
    "кибербезопас", "security",
    "робототех", "электроник", "радиоэлектроник",
    "хакатон", "hackathon", "митап", "meetup",
    "прототипирование приложений",
    "айтишник", "айтишников",
    "код", "code",
]

# Слабые маркеры: сами по себе могут давать мусор
WEAK_IT = [
    "ии", "искусственный интеллект", "нейросет", "deepseek",
    "цифров", "технолог", "алгоритм", "автоматизац",
]

# Явно плохой контекст: если он есть, событие режется
BAD_CONTEXT = [
    "театр", "драматург", "сказк", "квест", "кино", "фильм",
    "музык", "концерт", "оркестр", "хор",
    "поэз", "литератур", "книга", "книжн", "писател", "архив",
    "искусств", "худож", "живопис", "иллюстратор", "арт-терап",
    "психолог", "психотерап", "консультирован",
    "инвестиции", "недвижим", "финансов", "денег",
    "ортодонт", "клиническ", "сустава", "медицин",
    "педагог", "учител", "школ", "школьн", "дошколь",
    "огэ", "инклюзи", "обучающихся", "детск", "детей",
    "гуманность", "философ",
    "урал драматург", "драматургии",
]

# Доверенные IT-организаторы
TRUSTED_IT_ORGS = [
    "coffeecode-event.timepad.ru",
]


def clean_html_to_text(value: Optional[str]) -> str:
    if not value:
        return ""
    text = html.unescape(value)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_timepad_datetime(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    try:
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)

        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)

        return dt.isoformat()
    except ValueError:
        return None


def build_location(location: Optional[Dict[str, Any]]) -> Optional[str]:
    if not location:
        return None

    parts = []
    city = location.get("city")
    address = location.get("address")

    if city:
        parts.append(str(city).strip())
    if address:
        parts.append(str(address).strip())

    result = ", ".join(part for part in parts if part)
    return result if result else None


def fetch_timepad_events(
    city: str = CITY,
    organization_ids: Optional[List[int]] = None,
    days_ahead: int = DAYS_AHEAD,
    limit: int = LIMIT,
) -> List[Dict[str, Any]]:
    all_events: List[Dict[str, Any]] = []
    skip = 0

    starts_at_min = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    starts_at_max = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")

    while True:
        params = {
            "limit": limit,
            "skip": skip,
            "cities": city,
            "starts_at_min": starts_at_min,
            "starts_at_max": starts_at_max,
            "fields": "location",
            "sort": "+starts_at",
        }

        if organization_ids:
            params["organization_ids"] = ",".join(str(x) for x in organization_ids)

        response = requests.get(
            TIMEPAD_API_URL,
            params=params,
            timeout=30,
            headers={
                "Authorization": f"Bearer {TIMEPAD_TOKEN}",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
        )

        print("DEBUG URL:", response.url)
        print("DEBUG STATUS:", response.status_code)

        if response.status_code != 200:
            print("DEBUG TEXT:", response.text[:1000])

        response.raise_for_status()

        data = response.json()
        values = data.get("values", [])

        if not values:
            break

        all_events.extend(values)

        if len(values) < limit:
            break

        skip += limit
        time.sleep(0.2)

    return all_events


def normalize_timepad_event(event: Dict[str, Any]) -> Dict[str, Any]:
    title = (event.get("name") or "").strip()

    description_short = clean_html_to_text(event.get("description_short"))
    description_html = event.get("description_html") or ""
    raw_description = description_html.strip()

    if description_short:
        description = description_short
    elif description_html:
        description = clean_html_to_text(description_html)
    else:
        description = title

    poster = event.get("poster_image") or {}
    image_url = poster.get("default_url")

    source_url = event.get("url")
    event_date = parse_timepad_datetime(event.get("starts_at"))
    location = build_location(event.get("location"))

    return {
        "source": "timepad",
        "title": title,
        "event_date": event_date,
        "description": description,
        "location": location,
        "source_url": source_url,
        "image_url": image_url,
        "raw_description": raw_description or description,
    }


def looks_like_it_event(event: Dict[str, Any]) -> bool:
    title = (event.get("title") or "").lower()
    description = (event.get("description") or "").lower()
    raw_description = (event.get("raw_description") or "").lower()
    source_url = (event.get("source_url") or "").lower()

    full_text = " ".join([title, description, raw_description])

    # ❌ жестко режем мусор
    if any(bad in full_text for bad in BAD_CONTEXT):
        return False

    # ❌ дополнительные точечные запреты
    if "код здоровья" in full_text:
        return False

    if "nail" in full_text or "маникюр" in full_text:
        return False

    if "агропромышлен" in full_text:
        return False

    # ✅ доверенные IT-организаторы
    if any(org in source_url for org in TRUSTED_IT_ORGS):
        return True

    # ✅ сильные IT слова
    if any(k in full_text for k in STRONG_IT):
        return True

    # ⚠️ слабые слова — только если их минимум 2
    weak_hits = sum(1 for k in WEAK_IT if k in full_text)
    if weak_hits >= 2:
        return True

    return False

def get_db_connection():
    return psycopg2.connect(
        dbname="eventmind",
        user="postgres",
        password="kokos2007",
        host="localhost",
        port="5432"
    )

def save_events_to_db(events: List[Dict[str, Any]]) -> None:
    conn = get_db_connection()
    cur = conn.cursor()

    for event in events:
        cur.execute("""
            INSERT INTO events (
                title,
                event_date,
                description,
                location,
                source,
                source_url,
                image_url,
                raw_description
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_url) DO NOTHING
        """, (
            event["title"],
            event["event_date"],
            event["description"],
            event["location"],
            event["source"],
            event["source_url"],
            event["image_url"],
            event["raw_description"]
        ))

    conn.commit()
    cur.close()
    conn.close()

def main() -> None:
    if TIMEPAD_TOKEN == "ТВОЙ_TIMEPAD_TOKEN":
        raise RuntimeError("Вставь TIMEPAD_TOKEN в переменную TIMEPAD_TOKEN")

    print("Получаю события из TimePad...")

    raw_events = fetch_timepad_events(
        city=CITY,
        organization_ids=ORGANIZATION_IDS,
        days_ahead=DAYS_AHEAD,
        limit=LIMIT,
    )

    normalized_events: List[Dict[str, Any]] = []

    for raw_event in raw_events:
        event = normalize_timepad_event(raw_event)

        if not event["title"]:
            continue
        if not event["source_url"]:
            continue
        if not looks_like_it_event(event):
            continue

        normalized_events.append(event)

    with open("timepad_events.json", "w", encoding="utf-8") as f:
        json.dump(normalized_events, f, ensure_ascii=False, indent=2)

    save_events_to_db(normalized_events)

    print(f"Готово. Сохранено событий: {len(normalized_events)}")
    print("Файл: timepad_events.json")
    print("События TimePad сохранены в PostgreSQL")


if __name__ == "__main__":
    main()
