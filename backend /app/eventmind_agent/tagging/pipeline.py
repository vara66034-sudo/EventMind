from typing import Dict, Any
import logging

from tagging.nlp_processor import clean_text
from tagging.tagger import Tagger
from tagging.embeddings import Embedder


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

        try:
            title = event.get("title", "")
            description = event.get("description", "")

            raw_text = f"{title} {description}".strip()

            # 1. очистка
            cleaned_text = clean_text(raw_text)

            # 2. теги
            tags = self.tagger.extract_tags(cleaned_text)

            # 3. embedding
            embedding = self.embedder.encode(cleaned_text)

            result = {
                "text": cleaned_text,
                "tags": tags,
                "embedding": embedding
            }

            return result

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return {
                "text": "",
                "tags": [],
                "embedding": []
            }
