from sentence_transformers import SentenceTransformer
from torch import Tensor

from app.core.logging_config import logger


class QueryProcessor:
    def __init__(self) -> None:
        logger.info("Initialising QueryProcessor with CLIP model...")
        self.model = SentenceTransformer("clip-ViT-B-32")

    def get_text_embedding(self, text: str) -> Tensor:
        """Generate embedding for a text query using CLIP model."""
        try:
            logger.info(f"Generating embedding for text query: '{text}'")
            return self.model.encode(text)
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            raise
