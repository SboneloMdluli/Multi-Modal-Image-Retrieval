import base64
from typing import List

from app.core.logging_config import logger
from app.schemas.search import SearchResponse, SearchResult
from app.services.faiss_service import FaissService
from app.services.feast_service import FeastService
from fastapi import HTTPException


def _normalise_distances(distances: List[float]) -> List[float]:
    """Normalize distances to [0, 1] range"""
    try:
        # Convert cosine similarity (-1 to 1) to distance (0 to 1)
        normalized = [(1 + d) / 2 for d in distances]
        logger.info(f"Normalized distances: {normalized}")
        return normalized
    except Exception as e:
        logger.error(f"Error normalizing distances: {e}")
        raise


class SearchService:
    def __init__(self):
        self.faiss_service = FaissService()
        self.feast_service = FeastService()

    async def search_by_text(self, query: str, k: int, faiss_index) -> SearchResponse:
        logger.info(f"Processing text search request - Query: '{query}', k: {k}")
        if faiss_index is None:
            raise HTTPException(status_code=500, detail="Search index not available")

        try:
            distances, indices = self.faiss_service.search(faiss_index, query, k)

            # Normalise distances to [0, 1]
            normalized_distances = _normalise_distances(distances[0])

            results = await self._process_search(
                distances=normalized_distances, indices=indices[0]
            )

            return SearchResponse(results=results)
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            raise

    async def _process_search(
        self, distances: List[float], indices: List[int]
    ) -> List[SearchResult]:
        """Process search results to return image data and similarity scores"""
        logger.info(f"Processing search results for {len(indices)} images")
        try:
            image_ids = [str(idx) for idx in indices]
            features = self.feast_service.get_online_features(image_ids)

            results = []
            for distance, image_data in zip(distances, features["image_data"]):
                if image_data:
                    # Convert image to base64
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    image_str = f"data:image/jpeg;base64,{base64_image}"

                    results.append(
                        SearchResult(
                            image_data=image_str,
                            similarity=float(0.2),  # Convert distance to similarity
                        )
                    )

            return results

        except Exception as e:
            logger.error(f"Error processing search results: {e}")
            raise
