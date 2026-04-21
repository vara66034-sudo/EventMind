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

    def extract_tags(self, text: str, top_n: int = 5, min_score: float = 0.45) -> List[str]:
        if not text or len(text.strip()) < 5:
            return []

        try:
            keywords = self.model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 1),  # Только одиночные слова
                stop_words=None,
                use_mmr=True,  # Разнообразие смыслов
                diversity=0.6,
                top_n=top_n * 2
            )

            # Фильтруем по весу (score)
            # kw[0] - само слово, kw[1] - уверенность модели
            valid_tags = [kw[0] for kw in keywords if kw[1] >= min_score]

            # Возвращаем ровно столько, сколько просили (или меньше)
            return valid_tags[:top_n]
        except Exception as e:
            logger.error(f"Tag extraction error: {e}")
            return []
