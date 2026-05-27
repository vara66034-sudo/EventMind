import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from gigachat import GigaChat
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VK_TOKEN = os.getenv("VK_TOKEN")
VK_API_VERSION = "5.199"
VK_API_BASE = "https://api.vk.com/method"

SAVE_TO_DB = os.getenv("SAVE_TO_DB", "false").lower() == "true"
POSTS_PER_GROUP = 50  # Уменьшил до 50, так как GigaChat делает качественный анализ
SLEEP_BETWEEN_REQUESTS = 0.35

COMMUNITIES = [
    "event162254678",
    "inachehackrussia",
    "event26276043",
    "posnews",
    "naumenjavameetup",
    "irit_rtf_urfu",
]

# Базовый стоп-лист, чтобы не тратить токены GigaChat на явный мусор
BAD_CONTENT_MARKERS = [
    "розыгрыш", "разыгрыш", "пиццы", "вакансия", "вакансии", 
    "стажировка", "стажировки", "трудоустройство", "ищем", "ищет", 
    "итоги", "подводим итоги", "фотоотчет", "отзывы", "завершился"
]

def clean_multiline_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\[club\d+\|([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[id\d+\|([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[(https?://[^\]|]+)\|([^\]]+)\]", r"\2", text)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def has_bad_content(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in BAD_CONTENT_MARKERS)

def extract_event_data_with_llm(text: str, post_date_ts: int) -> dict:
    post_dt = datetime.fromtimestamp(post_date_ts)

    # ОБНОВЛЕННЫЙ ПРОМПТ: Умная работа с годами
    system_prompt = f"""Проанализируй текст и извлеки информацию о мероприятии. 
    Дата публикации поста: {post_dt.strftime('%Y-%m-%d')}. Текущий год — 2026.
    ПРАВИЛО ГОДА: Если год мероприятия не указан в тексте явно, обязательно используй год из "Даты публикации поста". НЕ ставь 2026 год для прошлогодних постов.
    Верни СТРОГО один JSON объект (не массив). Без markdown, без лишних слов.
    1. "title": Короткое название мероприятия (Если новость или мусор - null).
    2. "event_date": Дата ISO 8601 (например "2026-06-15T19:00:00"). Если даты нет - null.
    3. "location": Место проведения. Если онлайн - "Онлайн".
    4. "is_online": true или false.
    5. "description": Краткое описание мероприятия (о чем оно, главные детали).
    Текст: {text[:3000]}"""

    try:
        with GigaChat(credentials=os.getenv("GIGACHAT_CREDENTIALS"), verify_ssl_certs=False) as giga:
            response = giga.chat({
                "model": "GigaChat-Max",
                "messages": [
                    {"role": "user", "content": system_prompt}
                ],
                "temperature": 0.1
            })

            response_text = response.choices[0].message.content
            response_text = response_text.strip().strip("`").removeprefix("json").strip()
            
            parsed_json = json.loads(response_text)
            
            if isinstance(parsed_json, list):
                if len(parsed_json) > 0:
                    return parsed_json[0]
                return {}
                
            return parsed_json

    except Exception as e:
        print(f"Ошибка при обращении к GigaChat: {e}")
        return {}

def is_future_event(date_str) -> bool:
    if not date_str or not isinstance(date_str, str): 
        return False
    try:
        clean_date = date_str.strip()
        event_date = datetime.fromisoformat(clean_date)
        return event_date > datetime.now(event_date.tzinfo)
    except ValueError: 
        return False

def vk_api_call(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    if not VK_TOKEN:
        raise RuntimeError("VK_TOKEN не найден в .env")
    payload = dict(params)
    payload["access_token"] = VK_TOKEN
    payload["v"] = VK_API_VERSION
    response = requests.get(f"{VK_API_BASE}/{method}", params=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"VK API error in {method}: {data['error']}")
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    return data["response"]

def get_group_info(domain: str) -> Dict[str, Any]:
    response = vk_api_call("groups.getById", {"group_ids": domain, "fields": "screen_name,name,description"})
    if isinstance(response, list): return response[0]
    if isinstance(response, dict):
        if "groups" in response and response["groups"]: return response["groups"][0]
        if "response" in response and response["response"]: return response["response"][0]
    raise RuntimeError(f"Не удалось получить данные группы {domain}: {response}")

def get_wall_posts(domain: str, limit: int = POSTS_PER_GROUP) -> List[Dict[str, Any]]:
    response = vk_api_call("wall.get", {"domain": domain, "count": limit, "filter": "owner"})
    return response.get("items", [])

def choose_best_photo_url(attachments: List[Dict[str, Any]]) -> Optional[str]:
    best_url = None
    best_area = -1
    for att in attachments or []:
        if att.get("type") != "photo": continue
        photo = att.get("photo", {})
        for size in photo.get("sizes", []):
            url = size.get("url")
            width = size.get("width", 0)
            height = size.get("height", 0)
            area = width * height
            if url and area > best_area:
                best_area = area
                best_url = url
    return best_url

def detect_parent_event(text: str, group_name: str = "") -> Optional[str]:
    low = text.lower()
    group_low = (group_name or "").lower()
    if "dump" in low or "dump" in group_low: return "dump_2026"
    if "фестиваль радиоэлектроники" in low or "радиофест" in low: return "radiofest_2026"
    if "пик айти" in low or "pik it" in low: return "pik_it"
    if "young&&yandex" in low or "young con" in low or "баттл вузов" in low: return "young_yandex_battle"
    return None

def build_dedupe_key(event: Dict[str, Any]) -> str:
    parent_event = event.get("parent_event")
    if parent_event:
        return f"parent_{parent_event}"
    title_key = str(event.get("title", "")).lower().strip()
    date_key = str(event.get("event_date", ""))[:10]
    return f"{title_key}_{date_key}"

def build_event(post: Dict[str, Any], group: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if post.get("marked_as_ads") == 1:
        return None

    # ИСПРАВЛЕНИЕ: Жестко отсекаем старые посты ДО нейросети (старше 60 дней)
    post_date_ts = post.get("date", 0)
    post_dt = datetime.fromtimestamp(post_date_ts)
    if post_dt < datetime.now() - timedelta(days=60):
        return None

    text = clean_multiline_text(post.get("text", ""))
    
    if not text or len(text) < 20 or has_bad_content(text):
        return None

    llm_data = extract_event_data_with_llm(text, post_date_ts)

    if not llm_data or not llm_data.get("title") or not llm_data.get("event_date"):
        return None

    if not is_future_event(llm_data.get("event_date")):
        return None

    post_id = post["id"]
    owner_id = post["owner_id"]
    
    return {
        "source": "vk",
        "group_domain": group.get("screen_name"),
        "group_name": group.get("name"),
        "title": llm_data["title"],
        "event_date": llm_data["event_date"].strip(),
        "description": llm_data.get("description", ""),
        "location": llm_data.get("location", "Не указано"),
        "is_online": llm_data.get("is_online", False),
        "parent_event": detect_parent_event(text, group.get("name", "")),
        "source_url": f"https://vk.com/wall{owner_id}_{post_id}",
        "image_url": choose_best_photo_url(post.get("attachments", [])),
        "raw_description": text,
        "post_published_at": post_dt.isoformat()
    }

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL не найден в .env")
    return psycopg2.connect(database_url)

def save_events_to_db(events: List[Dict[str, Any]]) -> None:
    if not events:
        print("Нет событий для сохранения в БД")
        return
    conn = get_db_connection()
    cur = conn.cursor()
    saved_count = 0
    try:
        for event in events:
            cur.execute("""
                INSERT INTO events (
                    title, event_date, description, location, 
                    source, source_url, image_url, raw_description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_url) DO NOTHING
            """, (
                event["title"][:255],
                event["event_date"],
                event["description"][:5000] if event["description"] else None,
                event["location"][:255] if event["location"] else None,
                event["source"],
                event["source_url"],
                event["image_url"],
                event["raw_description"][:10000] if event["raw_description"] else None,
            ))
            saved_count += 1
        conn.commit()
        print(f"Всего обработано для сохранения: {saved_count}")
    except Exception as e:
        conn.rollback()
        print("Ошибка при сохранении в БД:", e)
    finally:
        cur.close()
        conn.close()

def clean_old_events() -> None:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM events WHERE event_date < CURRENT_DATE")
        deleted_count = cur.rowcount
        conn.commit()
        if deleted_count > 0:
            print(f"Удалено неактуальных событий из БД: {deleted_count}")
    except Exception as e:
        conn.rollback()
        print("Ошибка при удалении старых событий:", e)
    finally:
        cur.close()
        conn.close()

def main() -> None:
    if not VK_TOKEN:
        raise RuntimeError("Добавь VK_TOKEN в .env")

    all_events: List[Dict[str, Any]] = []
    seen_keys: Set[str] = set()

    for domain in COMMUNITIES:
        print(f"Обрабатываю сообщество: {domain}")
        try:
            group = get_group_info(domain)
            posts = get_wall_posts(domain)

            before_count = len(all_events)

            for post in posts:
                event = build_event(post, group)
                if not event:
                    continue

                dedupe_key = build_dedupe_key(event)
                if dedupe_key in seen_keys:
                    continue

                seen_keys.add(dedupe_key)
                all_events.append(event)
                print(f"  ✅ НАЙДЕНО СОБЫТИЕ: {event['title']}")

            print(f"  Добавлено новых событий: {len(all_events) - before_count}\n")

        except Exception as e:
            print(f"  ⚠️ Ошибка в {domain}: {repr(e)}")

    all_events.sort(key=lambda x: x.get("event_date") or "")

    output_path = os.path.join(BASE_DIR, "vk_events.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    if SAVE_TO_DB:
        save_events_to_db(all_events)
        clean_old_events()
    else:
        print("Сохранение в PostgreSQL отключено (установите SAVE_TO_DB=true)")

    print(f"\n🎉 Готово. Извлечено событий: {len(all_events)}")
    print(f"Файл сохранен: {output_path}")

if __name__ == "__main__":
    main()
