import logging
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger('EventMind.LLM')

class GigaChatService:
    def __init__(self, credentials: str):
        # credentials - это ваш авторизационный токен от Сбер GigaChat
        self.credentials = credentials

    def ask_ai_question(self, question: str, context_events: List[Dict] = None) -> str:
        """Отвечает на произвольный вопрос пользователя, учитывая контекст мероприятий"""
        
        events_context = ""
        if context_events:
            events_context = "Вот список актуальных мероприятий, которые есть в нашей базе:\n"
            # Берем до 20 событий для более широкого контекста
            for i, event in enumerate(context_events[:20], 1):
                date_str = event.get('date_begin', 'скоро')
                location = event.get('location', 'место не указано')
                events_context += f"- {event['name']} (Дата: {date_str}, Место: {location})\n"

        prompt = f"""
        Ты — EventMind AI, умный и дружелюбный ассистент по мероприятиям. Твоя задача — помогать пользователям находить интересные события в простом, человеческом диалоге.
        
        СЕГОДНЯШНЯЯ ДАТА: {datetime.now().strftime('%Y-%m-%d')}
        
        Пользователь задал вопрос: "{question}"
        
        {events_context}
        
        Твоя задача:
        1. Ответить на вопрос пользователя, используя список мероприятий выше.
        2. Если пользователь спрашивает про конкретный месяц (например, май), выбери из списка все события, которые пройдут в этом месяце.
        3. Если в списке нет подходящих событий, честно скажи об этом, но предложи ближайшие интересные варианты.
        4. Отвечай дружелюбно, как в обычном разговоре. 
        5. ВАЖНО: Не используй хештеги (#), markdown-заголовки или другие лишние символы форматирования. Твой ответ должен выглядеть как обычное сообщение от человека.
        6. Будь краток, но информативен.
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
            return "Извините, я временно не могу ответить на ваш вопрос. Пожалуйста, попробуйте позже."

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
        Твоя задача — порекомендовать пользователю события в формате личного сообщения. Я уже проверил его расписание, и эти события точно попадают в его свободное время!
        
        Интересы пользователя: {interests_text}
        
        Список подходящих событий:
        {events_text}
        
        Напиши короткое (до 3-4 абзацев), теплое сообщение. Скажи, что ты проанализировал его расписание и нашел отличные варианты. Кратко объясни, почему эти события ему понравятся, опираясь на его интересы. 
        ВАЖНО: Не используй хештеги (#), markdown или спецсимволы. Пиши просто и человечно. Не выдумывай факты и даты.
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
        # Используем ключ, предоставленный пользователем
        credentials = "MDE5ZDMyYjAtMGNhMC03MzY5LTliNzMtOWI0MWU1NzY1MWM2OjAzMjIxN2IyLTA0MWUtNGU4Zi1hMGI4LTljMjUyNTMxYTc5Zg=="
        _llm_instance = GigaChatService(credentials=credentials)
    return _llm_instance
