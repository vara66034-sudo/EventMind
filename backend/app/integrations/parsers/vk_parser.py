import json
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import joblib
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join("backend", "ml", "artifacts", "event_classifier.joblib")

VK_TOKEN = os.getenv("VK_TOKEN")
VK_API_VERSION = "5.199"
VK_API_BASE = "https://api.vk.com/method"

SAVE_TO_DB = os.getenv("SAVE_TO_DB", "false").lower() == "true"
POSTS_PER_GROUP = 100
SLEEP_BETWEEN_REQUESTS = 0.35
ML_THRESHOLD = 0.62

COMMUNITIES = [
    "event162254678",
    "stokrat_ekb",
    "analysts_mitap",
    "inachehackrussia",
    "event26276043",
    "aiesec_ekaterinburg",
    "posnews",
    "gamedevekb",
    "ussc_group",
    "naumenjavameetup",
    "irit_rtf_urfu",
]

MONTHS = {
    "января": 1, "январь": 1,
    "февраля": 2, "февраль": 2,
    "марта": 3, "март": 3,
    "апреля": 4, "апрель": 4,
    "мая": 5,
    "июня": 6, "июнь": 6,
    "июля": 7, "июль": 7,
    "августа": 8, "август": 8,
    "сентября": 9, "сентябрь": 9,
    "октября": 10, "октябрь": 10,
    "ноября": 11, "ноябрь": 11,
    "декабря": 12, "декабрь": 12,
}

DATE_DDMMYYYY_RE = re.compile(
    r"\b(?P<day>[0-3]?\d)[./](?P<month>[01]?\d)(?:[./](?P<year>\d{2,4}))?"
    r"(?:\s*(?:в|с|c)?\s*(?P<hour>[0-2]?\d)[:.](?P<minute>[0-5]\d))?",
    re.IGNORECASE,
)

DATE_TEXTUAL_RE = re.compile(
    r"\b(?P<day>[0-3]?\d)\s+"
    r"(?P<month>январ[ья]|феврал[ья]|март[а]?|апрел[ья]|ма[йя]|июн[ья]|июл[ья]|"
    r"август[а]?|сентябр[ья]|октябр[ья]|ноябр[ья]|декабр[ья])"
    r"(?:\s+(?P<year>\d{4}))?"
    r"(?:\s*(?:в|с|c)?\s*(?P<hour>[0-2]?\d)[:.](?P<minute>[0-5]\d))?",
    re.IGNORECASE,
)

TIME_RE = re.compile(r"\b([01]?\d|2[0-3])[:.]([0-5]\d)\b")

ADDRESS_RE = re.compile(
    r"\b(?:ул\.?\s*)?[А-ЯЁA-Z][а-яёa-z]+(?:\s+[А-ЯЁA-Z][а-яёa-z]+)*,\s*\d+[А-Яа-яA-Za-z/-]*\b"
)
MIRA_RE = re.compile(r"\bМира,\s*\d+\b", re.IGNORECASE)
URFU_RE = re.compile(r"\b(?:ГУК\s+)?УрФУ\b", re.IGNORECASE)
PARK_RE = re.compile(r"\bПарк\s+[А-ЯЁ][а-яё]+\b")
BC_RE = re.compile(r"\bБЦ\s+[«\"].+?[»\"]", re.IGNORECASE)

EXPO_RE = re.compile(r"\b(?:Екатеринбург[- ]Экспо|Экспо[- ]Екатеринбург|Екатеринбург-ЭКСПО)\b", re.IGNORECASE)
EKB_EXPO_RE = re.compile(r"\b(?:ЭКСПО\s*Екатеринбург|Екатеринбург\s*ЭКСПО|Екатеринбург-Экспо)\b", re.IGNORECASE)
EXPO_WORD_RE = re.compile(r"\bЭкспо\b", re.IGNORECASE)
GUK_RE = re.compile(r"\bГУК\b", re.IGNORECASE)
GAGARIN_RE = re.compile(r"\bФОК\s+[«\"]Гагаринский[»\"]\b", re.IGNORECASE)

BAD_CONTENT_MARKERS = [
    "розыгрыш",
    "разыгрыш",
    "пиццы",
    "вакансия",
    "вакансии",
    "стажировка",
    "стажировки",
    "трудоустройство",
    "ищем",
    "ищет",
    "открыт набор на стажировку",
    "горящие вакансии",
    "итоги",
    "подводим итоги",
    "фотоотчет",
    "фотоотчёт",
    "отчет",
    "отчёт",
    "отзывы",
    "спасибо всем",
    "как это было",
    "ищите себя на фото",
    "альбом",
    "победителями стали",
    "завершился",
    "завершился этап",
    "матпомощь",
    "материальную поддержку",
    "подача заявлений",
    "новое положение",
    "график приема",
    "приема заявлений",
]

TITLE_BAD_STARTS = [
    "друзья",
    "всем привет",
    "привет",
    "коллеги",
    "делимся",
    "напоминаем",
    "спасибо",
    "как это было",
    "подводим итоги",
    "итоги",
    "уже завтра",
    "бежим вас радовать",
    "пойдем",
    "ставьте",
    "ждём всех",
    "продолжаем",
    "еще один",
    "ещё один",
    "до конференции осталось",
    "ребята, привет",
    "что можно выиграть",
    "как устроено",
    "подготовка к",
    "удачи,",
    "совсем скоро",
    "чтобы узнать чуть больше",
    "удачи, наши",
    "подготовка к",
]

EVENT_MARKERS = [
    "митап", "meetup", "конференц", "лекци", "воркшоп", "мастер-класс",
    "хакатон", "hackathon", "стартап", "startup", "интенсив", "семинар",
    "форум", "ивент", "event", "нетворкинг", "дискуссия", "питч",
    "стрим", "олимпиада", "кибертурнир", "паблик-толк", "лекция",
    "день открытых дверей", "регистрация", "программа", "выступит",
    "состоится", "пройдет", "пройдёт", "приходите", "встречаемся",
]

MODEL = None
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)
else:
    print(f"Предупреждение: ML-модель не найдена по пути {MODEL_PATH}. Будет работать только rule-based фильтр.")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\[club\d+\|([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[id\d+\|([^\]]+)\]", r"\1", text)
    text = re.sub(r"\[(https?://[^\]|]+)\|([^\]]+)\]", r"\2", text)
    text = re.sub(r"\s+", " ", text.replace("\xa0", " "))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
    response = vk_api_call(
        "groups.getById",
        {
            "group_ids": domain,
            "fields": "screen_name,name,description"
        }
    )

    if isinstance(response, list):
        return response[0]

    if isinstance(response, dict):
        if "groups" in response and response["groups"]:
            return response["groups"][0]
        if "response" in response and response["response"]:
            return response["response"][0]

    raise RuntimeError(f"Не удалось получить данные группы {domain}: {response}")


def get_wall_posts(domain: str, limit: int = POSTS_PER_GROUP) -> List[Dict[str, Any]]:
    response = vk_api_call(
        "wall.get",
        {
            "domain": domain,
            "count": limit,
            "filter": "owner",
        }
    )
    return response.get("items", [])


def choose_best_photo_url(attachments: List[Dict[str, Any]]) -> Optional[str]:
    best_url = None
    best_area = -1

    for att in attachments or []:
        if att.get("type") != "photo":
            continue

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


def has_bad_content(text: str) -> bool:
    low = text.lower()
    return any(marker in low for marker in BAD_CONTENT_MARKERS)


def looks_like_event(text: str) -> bool:
    text = clean_multiline_text(text).lower()
    if not text:
        return False

    if has_bad_content(text):
        return False

    has_keyword = any(word in text for word in EVENT_MARKERS)
    has_date = bool(
        DATE_DDMMYYYY_RE.search(text)
        or DATE_TEXTUAL_RE.search(text)
        or "сегодня" in text
        or "завтра" in text
    )
    has_action = any(word in text for word in [
        "регистрация",
        "билеты",
        "участие",
        "подать заявку",
        "приходите",
        "ждём вас",
        "ждем вас",
        "состоится",
        "пройдет",
        "пройдёт",
        "встречаемся",
    ])

    return (has_keyword and has_date) or (has_date and has_action)


def ml_is_event(text: str, threshold: float = ML_THRESHOLD) -> bool:
    if MODEL is None:
        return False
    if not text or not text.strip():
        return False
    proba = MODEL.predict_proba([clean_text(text)])[0][1]
    return proba >= threshold


def extract_place(text: str) -> Optional[str]:
    text = clean_multiline_text(text)

    line_patterns = [
        r"(?:где|место|локация|адрес)\s*[:\-]\s*(.+)",
        r"(?:по адресу)\s+(.+?)(?:[.!?\n]|$)",
        r"📍\s*(?:место\s*[:\-]?\s*)?(.+)",
    ]

    bad_markers = [
        "ссылка", "регистрация", "подайте заявку", "пройдите",
        "vk.cc", "http", "https", "leader-id", "telegram", "t.me"
    ]

    for pattern in line_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for place in matches:
            place = place.split("\n")[0].strip(" .,-:;!\"'“”")
            place = re.sub(r"\b\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?\b.*$", "", place).strip()
            place = re.sub(r"\b\d{1,2}:\d{2}\b.*$", "", place).strip()

            if not place or len(place) < 4:
                continue

            low = place.lower()
            if any(marker in low for marker in bad_markers):
                continue

            return place[:255]

    candidates = []

    mira_match = MIRA_RE.search(text)
    if mira_match:
        candidates.append(mira_match.group(0))

    address_match = ADDRESS_RE.search(text)
    if address_match:
        candidates.append(address_match.group(0))

    urfu_match = URFU_RE.search(text)
    if urfu_match:
        candidates.append(urfu_match.group(0))

    park_match = PARK_RE.search(text)
    if park_match:
        candidates.append(park_match.group(0))

    bc_match = BC_RE.search(text)
    if bc_match:
        candidates.append(bc_match.group(0))

    expo_match = EXPO_RE.search(text)
    if expo_match:
        candidates.append(expo_match.group(0))

    ekb_expo_match = EKB_EXPO_RE.search(text)
    if ekb_expo_match:
        candidates.append(ekb_expo_match.group(0))

    expo_word_match = EXPO_WORD_RE.search(text)
    if expo_word_match:
        candidates.append(expo_word_match.group(0))

    guk_match = GUK_RE.search(text)
    if guk_match:
        candidates.append(guk_match.group(0))

    gagarin_match = GAGARIN_RE.search(text)
    if gagarin_match:
        candidates.append(gagarin_match.group(0))

    if candidates:
        joined = ", ".join(dict.fromkeys(candidates))
        return joined[:255]

    return None


def parse_event_datetime(text: str, post_ts: int) -> Optional[str]:
    text = clean_multiline_text(text)
    post_dt = datetime.fromtimestamp(post_ts)
    now = datetime.now()

    priority_lines = []
    for line in text.split("\n"):
        low = line.lower()
        if any(word in low for word in [
            "когда", "дата", "время", "состоится", "пройдет", "пройдёт",
            "встреча", "митап", "конференция", "форум", "лекция",
            "мастер-класс", "хакатон", "фестиваль", "финал",
            "встречаемся", "приходите", "регистрация"
        ]):
            priority_lines.append(line)

    search_texts = priority_lines + [text]

    for chunk in search_texts:
        match = DATE_DDMMYYYY_RE.search(chunk)
        if match:
            day = int(match.group("day"))
            month = int(match.group("month"))
            year = match.group("year")
            hour = int(match.group("hour")) if match.group("hour") else 0
            minute = int(match.group("minute")) if match.group("minute") else 0

            if not (1 <= month <= 12 and 1 <= day <= 31):
                continue

            if year:
                year_int = int(year)
                if year_int < 100:
                    year_int += 2000
            else:
                year_int = post_dt.year
                try:
                    candidate = datetime(year_int, month, day, hour, minute)
                    if candidate < post_dt - timedelta(days=30):
                        year_int += 1
                except ValueError:
                    continue

            try:
                return datetime(year_int, month, day, hour, minute).isoformat()
            except ValueError:
                continue

        match = DATE_TEXTUAL_RE.search(chunk.lower())
        if match:
            day = int(match.group("day"))
            month_name = match.group("month").lower()
            month = MONTHS.get(month_name)
            year = int(match.group("year")) if match.group("year") else post_dt.year
            hour = int(match.group("hour")) if match.group("hour") else 0
            minute = int(match.group("minute")) if match.group("minute") else 0

            if not month or not (1 <= day <= 31):
                continue

            try:
                candidate = datetime(year, month, day, hour, minute)
                if not match.group("year") and candidate < post_dt - timedelta(days=30):
                    candidate = datetime(year + 1, month, day, hour, minute)
                return candidate.isoformat()
            except ValueError:
                continue

    lower = text.lower()

    if "сегодня" in lower:
        tm = TIME_RE.search(text)
        hour = int(tm.group(1)) if tm else 0
        minute = int(tm.group(2)) if tm else 0
        return datetime(post_dt.year, post_dt.month, post_dt.day, hour, minute).isoformat()

    if "завтра" in lower:
        base = post_dt + timedelta(days=1)
        tm = TIME_RE.search(text)
        hour = int(tm.group(1)) if tm else 0
        minute = int(tm.group(2)) if tm else 0
        return datetime(base.year, base.month, base.day, hour, minute).isoformat()

    return None


def normalize_title(title: str) -> str:
    title = clean_text(title).lower()
    title = re.sub(r"https?://\S+", "", title)
    title = re.sub(r"clck\.ru/\S+", "", title)
    title = re.sub(r"vk\.cc/\S+", "", title)
    title = re.sub(r"[^\wа-яё\s-]", " ", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def normalize_place(place: Optional[str]) -> str:
    if not place:
        return ""
    place = clean_text(place).lower()
    place = re.sub(r"[^\wа-яё\s,.-]", " ", place, flags=re.IGNORECASE)
    place = re.sub(r"\s+", " ", place).strip()
    return place


def extract_title(text: str, group_name: str = "") -> str:
    text = clean_multiline_text(text)
    lines = [line.strip(" -–—•\t✨💡📍🗓️⏰‼️👉🖇️🚀💙💚🤪😋😱✏️🔥❤☺😉") for line in text.split("\n") if line.strip()]

    if not lines:
        return "Без названия"

    weak_title_starts = [
        "друзья",
        "всем привет",
        "привет",
        "коллеги",
        "делимся",
        "напоминаем",
        "спасибо",
        "как это было",
        "подводим итоги",
        "итоги",
        "уже завтра",
        "бежим вас радовать",
        "пойдем",
        "ставьте",
        "ждём всех",
        "продолжаем",
        "еще один",
        "ещё один",
        "до конференции осталось",
        "ребята, привет",
        "чтобы узнать чуть больше",
        "удачи, наши",
        "подготовка к",
        "что можно выиграть",
        "как устроено",
        "читай информацию в картинках",
    ]

    strong_patterns = [
        "митап", "конферен", "форум", "хакатон", "баттл", "турнир",
        "конкурс", "фестиваль", "олимпиад", "марафон", "лекци",
        "мастер-класс", "воркшоп", "интенсив", "радиофест",
        "dump", "пик айти", "young", "регистрация",
    ]

    candidates = []

    for idx, line in enumerate(lines[:6]):
        low = line.lower().strip()

        if len(low) < 5:
            continue

        if re.fullmatch(r"[\d\s₽.,:;!?\-—]+", low):
            continue

        if any(low.startswith(prefix) for prefix in weak_title_starts):
            continue

        score = 0

        if any(pat in low for pat in strong_patterns):
            score += 3

        if DATE_DDMMYYYY_RE.search(low) or DATE_TEXTUAL_RE.search(low):
            score += 2

        if "пройдет" in low or "пройдёт" in low or "состоится" in low:
            score += 2

        if len(low) <= 140:
            score += 1

        if idx == 0:
            score += 1

        candidates.append((score, line))

    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        best = candidates[0][1]
        return best[:140]

    return lines[0][:140]

def detect_parent_event(text: str, group_name: str = "") -> Optional[str]:
    low = clean_text(text).lower()
    group_low = (group_name or "").lower()

    if "dump" in low or "dump" in group_low:
        return "dump_2026"

    if "фестиваль радиоэлектроники" in low or "радиофест" in low:
        return "radiofest_2026"

    if "пик айти" in low or "pik it" in low:
        return "pik_it"

    if "young&&yandex" in low or "young con" in low or "баттл вузов" in low:
        return "young_yandex_battle"

    return None

def is_future_event(event_date: Optional[str]) -> bool:
    if not event_date:
        return False

    try:
        dt = datetime.fromisoformat(event_date)
        return dt >= datetime.now() - timedelta(days=1)
    except ValueError:
        return False


def build_dedupe_key(event: Dict[str, Any]) -> Tuple[str, str]:
    parent_event = event.get("parent_event")
    if parent_event:
        return ("parent_event", parent_event)

    title_key = normalize_title(event.get("title", ""))
    event_date = event.get("event_date", "")
    date_key = event_date[:10] if event_date else ""
    return (title_key, date_key)


def build_event(post: Dict[str, Any], group: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if post.get("marked_as_ads") == 1:
        return None

    raw_text = post.get("text", "") or ""
    text = clean_multiline_text(raw_text)

    if not text or len(text) < 20:
        return None

    if has_bad_content(text):
        return None

    rule_pred = looks_like_event(text)
    ml_pred = ml_is_event(text, threshold=ML_THRESHOLD)

    if not (rule_pred or ml_pred):
        return None

    event_date = parse_event_datetime(text, post.get("date", 0))
    if not is_future_event(event_date):
        return None

    title = extract_title(text, group.get("name", ""))
    place = extract_place(text)
    parent_event = detect_parent_event(text, group.get("name", ""))


    low = text.lower()
    if "реклама." in low or "erid:" in low or "инн:" in low:
        return None

    post_id = post["id"]
    owner_id = post["owner_id"]

    return {
        "source": "vk",
        "group_domain": group.get("screen_name"),
        "group_name": group.get("name"),
        "title": title,
        "event_date": event_date,
        "description": text[:3000],
        "place": place,
        "parent_event": parent_event,
        "source_url": f"https://vk.com/wall{owner_id}_{post_id}",
        "image_url": choose_best_photo_url(post.get("attachments", [])),
        "raw_description": text,
        "post_published_at": datetime.fromtimestamp(post["date"]).isoformat(),
        "ml_used": MODEL is not None,
        "ml_threshold": ML_THRESHOLD,
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
                event["title"][:255] if event["title"] else None,
                event["event_date"],
                event["description"][:5000] if event["description"] else None,
                event["place"][:255] if event["place"] else None,
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
        print("Ошибка при сохранении в БД:")
        print(e)
        raise
    finally:
        cur.close()
        conn.close()


def main() -> None:
    if not VK_TOKEN:
        raise RuntimeError("Добавь VK_TOKEN в .env")

    all_events: List[Dict[str, Any]] = []
    seen_keys: Set[Tuple[str, str, str]] = set()

    for domain in COMMUNITIES:
        print(f"Обрабатываю: {domain}")
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

            print(f"  Добавлено новых событий: {len(all_events) - before_count}")
            print(f"  Всего событий: {len(all_events)}")

        except Exception as e:
            import traceback
            print(f"  Ошибка в {domain}: {repr(e)}")
            traceback.print_exc()

    all_events.sort(key=lambda x: x.get("event_date") or "")

    output_path = os.path.join(BASE_DIR, "events.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    if SAVE_TO_DB:
        save_events_to_db(all_events)
    else:
        print("Сохранение в PostgreSQL отключено")

    print(f"\nГотово. Сохранено событий в JSON: {len(all_events)}")
    print(f"Файл: {output_path}")


if __name__ == "__main__":
    main()
