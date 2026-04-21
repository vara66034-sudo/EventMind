from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

class Embedder:
    """
    Генерация embeddings для текста
    """

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def encode(self, text: str) -> List[float]:
        if not text:
            return []

        try:
            vector = self.model.encode(text)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []
