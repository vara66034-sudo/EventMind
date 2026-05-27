import os
import re
import json
import asyncio
import pandas as pd
import requests
import urllib3
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
TG_SESSION = os.getenv("TG_SESSION")
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")

OUTPUT_JSON = "telegram_events.json"

# Создаем папку для картинок, если её нет
os.makedirs("images", exist_ok=True)

CHANNEL_IT_ONLINE = 'iteventsjuniors'
CHANNELS_GENERAL = [
    'choiceekb', 'ekbnash', 'davaicxodim_ekb', 
    'veermallekb', 'bceekb'
]

def get_gigachat_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e',
        'Authorization': f'Basic {GIGACHAT_CREDENTIALS}'
    }
    response = requests.post(url, headers=headers, data='scope=GIGACHAT_API_PERS', verify=False)
    return response.json()['access_token']

def extract_event_with_gigachat(text: str, token: str) -> dict:
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    prompt = f"""Проанализируй текст и извлеки информацию о мероприятии. 
    ВНИМАНИЕ: Текущий год — 2026. Если год не указан явно, обязательно используй 2026.
    Верни СТРОГО один JSON объект (не массив). Без markdown, без лишних слов.
    1. "title": Короткое название мероприятия (Если новость - null).
    2. "event_date": Дата ISO 8601 (например "2026-06-15"). Если нет - null.
    3. "location": Место проведения. Если онлайн - "Онлайн".
    4. "is_online": true или false.
    5. "description": Краткое описание мероприятия (о чем оно, главные детали).
    Текст: {text}"""
    
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    payload = json.dumps({"model": "GigaChat-Max", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1})
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False)
        raw_content = response.json()['choices'][0]['message']['content'].replace("```json", "").replace("```", "").strip()
        parsed_json = json.loads(raw_content)
        
        if isinstance(parsed_json, list):
            if len(parsed_json) > 0:
                return parsed_json[0]
            return None
            
        return parsed_json
    except Exception as e:
        return None

def is_future_event(date_str) -> bool:
    if not date_str or not isinstance(date_str, str): 
        return False
    try:
        clean_date = date_str.strip()
        event_date = datetime.fromisoformat(clean_date)
        return event_date > datetime.now(event_date.tzinfo)
    except ValueError: 
        return False

async def fetch_telegram_posts():
    client = TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH)
    await client.connect()
    it_posts, general_posts = [], []
    
    print(f"Читаем IT-канал: @{CHANNEL_IT_ONLINE}...")
    try:
        async for message in client.iter_messages(CHANNEL_IT_ONLINE, limit=50):
            if message.text:
                # Скачиваем картинку
                image_path = None
                if message.photo:
                    image_path = await client.download_media(message.photo, file=f"images/{CHANNEL_IT_ONLINE}_{message.id}.jpg")
                
                it_posts.append({
                    "source": f"t.me/{CHANNEL_IT_ONLINE}/{message.id}", 
                    "text": message.text,
                    "image_url": image_path
                })
    except Exception as e: print(f"⚠️ Ошибка {CHANNEL_IT_ONLINE}: {e}")

    for channel in CHANNELS_GENERAL:
        print(f"Читаем канал: {channel}...")
        try:
            entity = channel.split('+')[-1] if '+' in channel else channel
            async for message in client.iter_messages(entity, limit=30):
                if message.text:
                    # Скачиваем картинку
                    image_path = None
                    if message.photo:
                        clean_channel_name = channel.replace("https://t.me/+", "private_")
                        image_path = await client.download_media(message.photo, file=f"images/{clean_channel_name}_{message.id}.jpg")

                    general_posts.append({
                        "source": f"t.me/{channel}/{message.id}", 
                        "text": message.text,
                        "image_url": image_path
                    })
        except Exception as e: print(f"⚠️ Ошибка {channel}: {e}")
    await client.disconnect()
    return it_posts, general_posts


# === ИСПРАВЛЕНИЕ: Обернули запуск в асинхронную функцию main() ===
async def main():
    it_posts, general_posts = await fetch_telegram_posts()
    print(f"\nСобрано сырых текстов: {len(it_posts)} ИТ, {len(general_posts)} городских.")

    posts_to_process = it_posts + general_posts
    print(f"\nЗапуск GigaChat ({len(posts_to_process)} постов)... Ждем.")
    token = get_gigachat_token()

    seen_titles = set()
    final_events = []

    for post in posts_to_process:
        event_data = extract_event_with_gigachat(post['text'], token)
        
        if not event_data or not isinstance(event_data, dict) or not event_data.get("title"): 
            continue
            
        title = event_data.get("title")

        if CHANNEL_IT_ONLINE in post['source'] and not event_data.get("is_online"): 
            continue
            
        if not is_future_event(event_data.get("event_date")): 
            continue

        if title in seen_titles:
            continue
            
        seen_titles.add(title)

        final_events.append({
            "source": "telegram", 
            "source_url": post["source"], 
            "title": title,
            "description": event_data.get("description", ""), 
            "location": event_data.get("location", "Не указано"), 
            "event_date": event_data.get("event_date").strip(),
            "is_online": event_data.get("is_online", False), 
            "image_url": post.get("image_url"), 
            "raw_description": post["text"] 
        })
        print(f"  ✅ ДОБАВЛЕНО: {title}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_events, f, indent=4, ensure_ascii=False)
    print(f"\n🎉 Успешно! Файл {OUTPUT_JSON} обновлен по новой схеме!")

# Запускаем главную функцию правильно для обычного Python
if __name__ == "__main__":
    asyncio.run(main())
