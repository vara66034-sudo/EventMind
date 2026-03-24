import logging
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from typing import List, Dict

logger = logging.getLogger('EventMind.LLM')

class GigaChatService:
    def __init__(self, credentials: str):
        # credentials - это ваш авторизационный токен от Сбер GigaChat
        # добавить токен
        self.credentials = credentials

    def generate_personal_advice(self, user_interests: List[str], top_events: List[Dict]) -> str:
        """Генерирует человечный текст с рекомендациями на основе расписания и интересов"""
        
        if not top_events:
            return "К сожалению, на ближайшее время подходящих событий в вашем расписании не найдено."

        # Формируем список событий для промпта
        events_text = ""
        for i, event in enumerate(top_events, 1):
            date_begin = event.get('date_begin', 'Время не указано')
            location = event.get('location', 'Место не указано')
            events_text += f"{i}. {event['name']} (Начало: {date_begin}, Место: {location})\n"

        interests_text = ", ".join(user_interests) if user_interests else "разные"

        # Системный промпт
        prompt = f"""
        Ты — умный и дружелюбный ИИ-ассистент по мероприятиям EventMind.
        Твоя задача — порекомендовать пользователю события. Я уже проверил его расписание, и эти события точно попадают в его свободное время!
        
        Интересы пользователя: {interests_text}
        
        Список подходящих событий:
        {events_text}
        
        Напиши короткое (до 3-4 абзацев), теплое сообщение. Скажи, что ты проанализировал его расписание и нашел отличные варианты. Кратко объясни, почему эти события ему понравятся, опираясь на его интересы. Не выдумывай факты и даты.
        """

        try:
            with GigaChat(credentials=self.credentials, verify_ssl_certs=False) as giga:
                payload = Chat(
                    messages=[
                        Messages(
                            role=MessagesRole.USER,
                            content=prompt
                        )
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )
                response = giga.chat(payload)
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GigaChat API Error: {e}")
            return "События подобраны, но я временно не могу сгенерировать персональное описание."

# Синглтон для сервиса
_llm_instance = None
def get_llm_service() -> GigaChatService:
    global _llm_instance
    if _llm_instance is None:
        # добавить токен
        _llm_instance = GigaChatService(credentials="ВАШ_АВТОРИЗАЦИОННЫЙ_ТОКЕН_GIGACHAT")
    return _llm_instance
