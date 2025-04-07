import numpy as np

from app.core.logging_config import logger
from app.core.query_processor import QueryProcessor


class FaissService:
    def __init__(self) -> None:
        self.query_processor = QueryProcessor()

    def search(
        self,
        index,
        query: str,
        top_k: int = 3,
    ) -> tuple[list[float], list[int]]:
        """Retrieve images based on a text query using FAISS index.

        Args:
        ----
            query: Text query to search for
            index: FAISS index for similarity search
            top_k: Number of similar images to retrieve

        Returns:
        -------
            Tuple containing the query and numpy array of similar indices
        """
        try:
            query_embeddings = self.query_processor.get_text_embedding(query)

            query_features = query_embeddings.astype(np.float32).reshape(1, -1)

            distances, indices = index.search(query_features, top_k)

            return distances[0], indices[0]

        except Exception as e:
            logger.error(f"Error in retrieve_similar_images: {e}")
            raise
