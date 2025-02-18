from typing import Tuple

import numpy as np
from app.core.logging_config import logger
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("clip-ViT-B-32")

    def retrieve_similar_images(
        self, query: str, index, top_k: int = 3
    ) -> Tuple[str, np.ndarray]:
        """
        Retrieve similar images based on a text query using FAISS index.

        Args:
            query: Text query to search for
            index: FAISS index for similarity search
            top_k: Number of similar images to retrieve

        Returns:
            Tuple containing the query and numpy array of similar indices
        """
        try:
            logger.info(f"Encoding query: '{query}'")
            query_features = self.model.encode(query)
            query_features = query_features.astype(np.float32).reshape(1, -1)

            logger.info(f"Performing similarity search with k={top_k}")
            distances, indices = index.search(query_features, top_k)

            logger.info(f"Found {len(indices[0])} similar images")
            return distances, indices

        except Exception as e:
            logger.error(f"Error in retrieve_similar_images: {e}")
            raise
