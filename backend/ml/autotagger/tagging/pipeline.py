from typing import Dict, Any
import logging

from tagging.nlp_processor import clean_text
from tagging.tagger import Tagger
from tagging.embeddings import Embedder
from tagging.taxonomy import ANCHOR_CATEGORIES
from tagging.taxonomy import SAFE_KEYWORDS


logger = logging.getLogger(__name__)


class TaggingPipeline:
    """
    Главный pipeline обработки события
    """

    def __init__(self):
        self.tagger = Tagger()
        self.embedder = Embedder()

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обрабатывает событие и возвращает:
        - очищенный текст
        - теги
        - embedding
        """

        title = event.get("title", "")
        description = event.get("description", "")
        raw_text = f"{title} {description}".strip()

        # 1. Очистка текста
        cleaned_text = clean_text(raw_text)

        # 2. Получаем теги от нейросети
        ml_tags = self.tagger.extract_tags(cleaned_text)

        # 3. Категории из жестких правил (ANCHOR_CATEGORIES)
        category_tags = []
        for category, keywords in ANCHOR_CATEGORIES.items():
            if any(kw in cleaned_text for kw in keywords):
                category_tags.append(category)

        # 4. ФИЛЬТРАЦИЯ (Самое важное!)
        # Мы оставляем ML-тег ТОЛЬКО если он входит в твой SAFE_KEYWORDS
        filtered_ml_tags = [tag for tag in ml_tags if tag in SAFE_KEYWORDS]

        # 5. Сборка финального списка
        # Объединяем категории по правилам и отфильтрованные ML-теги
        final_tags = list(dict.fromkeys(category_tags + filtered_ml_tags))

        # Если после фильтрации список пуст, можно оставить 1-2 лучших ML-тега
        if not final_tags and ml_tags:
            final_tags = ml_tags[:1]

            # 6. Эмбеддинг
        embedding = self.embedder.encode(cleaned_text)

        return {
            "text": cleaned_text,
            "tags": final_tags,
            "embedding": embedding
        }
