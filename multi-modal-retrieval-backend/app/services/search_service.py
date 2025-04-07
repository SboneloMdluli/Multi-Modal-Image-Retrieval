import base64
from io import BytesIO
from typing import Any

from fastapi import HTTPException
from PIL import Image

from app.core.logging_config import logger
from app.schemas.search import SearchResponse, SearchResult
from app.services.faiss_service import FaissService
from app.services.feast_service import FeastService
from app.services.image_service import ImageService


def _base64_to_pil_image(image_bytes: bytes) -> Image.Image:
    """Convert base64 encoded image bytes to a PIL Image object.

    Args
    ----------
        image_bytes (bytes): The image data in bytes format.

    Returns
    -------
        Image.Image: A PIL Image object created from the input bytes.
    """
    buffer = BytesIO(image_bytes)
    return Image.open(buffer)


class SearchService:
    """Service for text and image-based search operations.

    This class integrates FAISS search, Feast storage, and image processing
    capabilities.
    """

    def __init__(self) -> None:
        """Initialize SearchService with required dependencies."""
        self.faiss_service = FaissService()
        self.feast_service = FeastService()
        self.image_service = ImageService()

    async def search_by_text(
        self,
        query: str,
        k: int,
        sort: bool,
        faiss_index: Any,
    ) -> SearchResponse:
        """Perform a text-based search for similar images.

        Args:
        ----
            query (str): The text query to search for.
            k (int): Number of results to return.
            sort (bool): Whether to sort results by similarity score.
            faiss_index (Any): The FAISS index to use for search.

        Returns:
        -------
            SearchResponse: Object containing search results with images and
                          metadata.

        Raises:
        ------
            HTTPException: If search index is not available.
            Exception: For other errors during search process.
        """
        logger.info(
            "Processing text search request - Query: '%s', k: %d",
            query,
            k,
        )
        if faiss_index is None:
            raise HTTPException(
                status_code=500,
                detail="Search index not available",
            )

        try:
            distances, indices = self.faiss_service.search(
                faiss_index,
                query,
                k,
            )

            results = await self._process_search(
                distances,
                indices,
            )
            results = (
                sorted(results, key=lambda x: x.distance) if sort else results
            )

            return SearchResponse(results=results)
        except Exception as e:
            logger.error("Error in text search: %s", e)
            raise

    async def _process_search(
        self,
        distances: list[float],
        indices: list[int],
    ) -> list[SearchResult]:
        """Process raw search results into formatted search results.

        This method retrieves image data for the search results, generates
        captions, and formats the response with base64-encoded images and
        similarity scores.

        Args:
        ----
            distances (List[float]): List of similarity scores for each result.
            indices (List[int]): List of indices for matched images.

        Returns:
        -------
            List[SearchResult]: Results with image data, scores, and captions.
        """
        logger.info("Processing search results for %d images", len(indices))
        try:
            image_ids: list[str] = [str(idx) for idx in indices]
            features: dict[str, Any] = self.feast_service.get_online_features(
                image_ids,
            )
            results = []

            images: list[Image.Image] = [
                _base64_to_pil_image(image) for image in features["image_data"]
            ]
            captions = self.image_service.generate_caption(images)

            for i, (distance, _idx, caption_idx) in enumerate(
                zip(distances, indices, captions, strict=False),
            ):
                image_data = features["image_data"][i]
                # Convert image to base64
                base64_image = base64.b64encode(image_data).decode("utf-8")
                image_str = f"data:image/jpeg;base64,{base64_image}"

                results.append(
                    SearchResult(
                        image_data=image_str,
                        distance=distance,
                        caption=caption_idx,
                    ),
                )

            return results

        except Exception as e:
            logger.error(f"Error processing search results: {e}")
            # Return empty results instead of raising to prevent crashes
            return []
