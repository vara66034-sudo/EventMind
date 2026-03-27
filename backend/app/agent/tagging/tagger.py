from keybert import KeyBERT
from typing import List
import logging


logger = logging.getLogger(__name__)


class Tagger:
    """
    Извлечение тегов с помощью нейросети (KeyBERT)
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            self.model = KeyBERT(model_name)
            logger.info(f"Tagger model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Error loading tagger model: {e}")
            raise

    def extract_tags(self, text: str, top_n: int = 5) -> List[str]:
        """
        Возвращает список тегов
        """

        if not text:
            return []

        try:
            keywords = self.model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words=None,   # multilingual
                top_n=top_n
            )

            # keywords: [("ai meetup", 0.82), ...]
            tags = [kw[0] for kw in keywords]

            return tags

        except Exception as e:
            logger.error(f"Tag extraction error: {e}")
            return []
