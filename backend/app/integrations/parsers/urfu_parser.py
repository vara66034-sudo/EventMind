import os
import json
import time
from datetime import datetime
from typing import Any, Dict, List
from gigachat import GigaChat
import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL")
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
SAVE_TO_DB = os.getenv("SAVE_TO_DB", "false").lower() == "true"

def extract_event_data_with_llm(text: str) -> dict:
    system_prompt = f"""Проанализируй текст и извлеки информацию о мероприятии. 
    ВНИМАНИЕ: Текущий год — 2026. Если год не указан явно, используй 2026.
    Верни СТРОГО один JSON объект (не массив). Без markdown, без лишних слов.
    1. "title": Короткое название мероприятия (Если новость или мусор - null).
    2. "event_date": Дата ISO 8601 (например "2026-06-15T19:00:00"). Если даты нет - null.
    3. "location": Место проведения. Если онлайн - "Онлайн".
    4. "is_online": true или false.
    5. "description": Краткое описание мероприятия (о чем оно, главные детали).
    Текст: {text[:3000]}"""

    try:
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, verify_ssl_certs=False) as giga:
            response = giga.chat({
                "model": "GigaChat-Max",
                "messages": [
                    {"role": "user", "content": system_prompt}
                ],
                "temperature": 0.1
            })

            response_text = response.choices[0].message.content.strip().strip("`").removeprefix("json").strip()
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

def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL не найден в .env")
    return psycopg2.connect(DATABASE_URL)

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
                event["description"][:5000] if event.get("description") else None,
                event["location"][:255] if event.get("location") else None,
                event["source"],
                event["source_url"],
                event.get("image_url"),
                event["raw_description"][:10000] if event.get("raw_description") else None,
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


class UrfuEventsScraperSmart:
    def __init__(self, main_url="https://urfu.ru/ru/events/"):
        self.main_url = main_url
        self.api_url = "https://urfu.ru/get-events/ru/"
        self.events = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.main_url,
            'Accept': '*/*'
        })

    def get_api_parameters(self):
        print(f"Сканируем страницу {self.main_url} для получения настроек API...")
        try:
            response = self.session.get(self.main_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            container = soup.find('div', class_='events-container')
            if not container:
                print("Не удалось найти контейнер событий.")
                return None
            params = {}
            for attr, value in container.attrs.items():
                if attr.startswith('data-'):
                    params[attr.replace('data-', '')] = value
            return params
        except requests.RequestException as e:
            print(f"Ошибка при получении страницы: {e}")
            return None

    def fetch_events_data(self, params, attempt=1):
        try:
            response = self.session.get(self.api_url, params=params, timeout=(10, 30))
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            if attempt < 3:
                time.sleep(3)
                return self.fetch_events_data(params, attempt + 1)
        except requests.RequestException as e:
            print(f"Сетевая ошибка: {e}")
        return None

    def parse_response(self, raw_response):
        html = raw_response
        if raw_response.strip().startswith('{'):
            try:
                data = json.loads(raw_response)
                html = data.get('html', data.get('content', raw_response))
            except json.JSONDecodeError:
                pass

        soup = BeautifulSoup(html, 'html.parser')
        event_cards = soup.select('.widget-event.event-item, .event-item')
        
        page_events = []
        for card in event_cards:
            title_link = card.select_one('p.title a, h3 a, .title a')
            if not title_link:
                title_link = card.find('a')
                if not title_link: continue

            title = " ".join(title_link.get_text().split())
            link = title_link.get('href', '').strip()
            if link.startswith('/'): link = "https://urfu.ru" + link

            date_tag = card.select_one('p.date, .date')
            date = " ".join(date_tag.get_text().split()) if date_tag else ""

            snippet_tag = card.select_one('div.snippet, .snippet')
            snippet = " ".join(snippet_tag.get_text().split()) if snippet_tag else ""
            
            img_tag = card.select_one('img')
            image_url = None
            if img_tag and img_tag.get('src'):
                image_url = img_tag.get('src')
                if image_url.startswith('/'): image_url = "https://urfu.ru" + image_url

            raw_text = f"Название: {title}\nДата: {date}\nОписание: {snippet}"
            
            # Пропускаем через Нейросеть
            llm_data = extract_event_data_with_llm(raw_text)
            
            if not llm_data or not llm_data.get("title") or not llm_data.get("event_date"):
                continue
                
            if not is_future_event(llm_data.get("event_date")):
                continue

            page_events.append({
                "source": "urfu",
                "source_url": link,
                "title": llm_data["title"],
                "event_date": llm_data["event_date"].strip(),
                "description": llm_data.get("description", ""),
                "location": llm_data.get("location", "Не указано"),
                "is_online": llm_data.get("is_online", False),
                "image_url": image_url,
                "raw_description": raw_text
            })
            print(f"  ✅ НАЙДЕНО СОБЫТИЕ УрФУ: {llm_data['title']}")

        return page_events

    def run(self):
        base_params = self.get_api_parameters()
        if not base_params:
            return

        print("\nНачинаем сбор событий УрФУ...")
        current_offset = 0

        # Ограничим, чтобы каждый день не гонять нейросеть по сотням старых постов
        while current_offset < 50: 
            base_params['offset'] = str(current_offset)
            print(f"--- Запрашиваем данные (сдвиг {current_offset}) ---")

            raw_response = self.fetch_events_data(base_params)
            if not raw_response:
                break

            html = raw_response
            if raw_response.strip().startswith('{'):
                try:
                    data = json.loads(raw_response)
                    html = data.get('html', data.get('content', raw_response))
                except json.JSONDecodeError:
                    pass
            soup = BeautifulSoup(html, 'html.parser')
            actual_count_on_page = len(soup.select('.widget-event.event-item, .event-item'))
            
            if actual_count_on_page == 0:
                break

            new_events = self.parse_response(raw_response)
            self.events.extend(new_events)
                
            current_offset += actual_count_on_page
            time.sleep(1)

        unique_events = {e["source_url"]: e for e in self.events}.values()
        unique_events_list = list(unique_events)

        output_path = os.path.join(BASE_DIR, "urfu_events.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(unique_events_list, f, ensure_ascii=False, indent=2)

        if SAVE_TO_DB:
            save_events_to_db(unique_events_list)
            clean_old_events()
        else:
            print("Сохранение в PostgreSQL отключено (установите SAVE_TO_DB=true)")

        print(f"\n🎉 ГОТОВО! Собрано и обработано: {len(unique_events_list)}.")


if __name__ == "__main__":
    scraper = UrfuEventsScraperSmart()
    scraper.run()
