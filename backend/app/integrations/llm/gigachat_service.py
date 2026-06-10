import logging
import os
import contextlib
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger('EventMind.LLM')


@contextlib.contextmanager
def _no_proxy():
    """Временно отключает системные прокси, чтобы GigaChat не падал на SOCKS4."""
    _proxy_keys = ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY',
                   'http_proxy', 'https_proxy', 'all_proxy')
    saved = {k: os.environ.pop(k, None) for k in _proxy_keys}
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v

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
            with _no_proxy():
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
            tags = event.get('tags', [])
            if isinstance(tags, list):
                tags_str = ', '.join(tags[:5]) if tags else 'нет тегов'
            else:
                tags_str = str(tags)
            description = (event.get('description') or '')[:200]
            events_text += f"{i}. {event['name']}\n   Теги: {tags_str}\n   Дата: {date_begin}, Место: {location}\n   Описание: {description}\n\n"

        interests_text = ", ".join(user_interests) if user_interests else "разные темы"

        # Системный промпт
        prompt = f"""
        Ты — умный и дружелюбный ИИ-ассистент по мероприятиям EventMind.
        
        Интересы пользователя: {interests_text}
        
        Список подобранных событий (с тегами и описанием):
        {events_text}
        
        Твоя задача — написать ОДИН живой текст-рекомендацию, обращаясь к пользователю на «ты».
        
        ОБЯЗАТЕЛЬНО для каждого события объясни:
        - Почему именно ОНО подходит данному пользователю (связь с его интересами: {interests_text})
        - Что конкретно он там найдёт или сможет сделать
        
        Пример хорошего формата:
        «Тебе нравится [интерес X], поэтому я выбрал [Название события 1] — там будет [конкретная причина, почему подходит]. Кроме того, обрати внимание на [Название события 2]: поскольку ты интересуешься [интерес Y], тебе точно понравится [что там будет]...»
        
        ПРАВИЛА ФОРМАТИРОВАНИЯ:
        - Не используй символы "|||", "---", Markdown-заголовки, хештеги (#)
        - Пиши связно, как живой человек, без сухого перечисления
        - Текст должен быть тёплым и мотивирующим
        - Упомяни каждое событие из списка
        """

        try:
            with _no_proxy():
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
        # Используем ключ из .env или дефолтный
        credentials = os.getenv("GIGACHAT_CREDENTIALS")
        if not credentials:
            raise RuntimeError("GIGACHAT_CREDENTIALS is not set in environment")
        _llm_instance = GigaChatService(credentials=credentials)
    return _llm_instance
