import numpy as np
from app.core.logging_config import logger
from sentence_transformers import SentenceTransformer


class QueryProcessor:
    def __init__(self):
        logger.info("Initialising QueryProcessor with CLIP model...")
        self.model = SentenceTransformer("clip-ViT-B-32")

    def get_text_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a text query using CLIP model"""
        try:
            logger.info(f"Generating embedding for text query: '{text}'")
            embedding = self.model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            raise
