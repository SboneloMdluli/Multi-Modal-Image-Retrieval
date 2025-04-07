from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.logging_config import logger
from app.dependencies.models import get_faiss_index
from app.schemas.search import SearchResponse
from app.services.feast_service import FeastService
from app.services.search_service import SearchService

router = APIRouter(
    prefix="/features",
    tags=["features"],
    responses={404: {"description": "Not found"}},
)

feature_service = FeastService()
search_service = SearchService()


@router.get("/search", response_model=SearchResponse)
async def search_images_by_text(
    query: str = Query(...),
    k: int = Query(default=3, ge=1),
    sort: bool = Query(default=True),
    faiss_index=Depends(get_faiss_index),
) -> SearchResponse:
    """Search for images using a text query.

    Args
    ----------
        query (str): The text query to search for
        k (int, optional): Number of results to return. Defaults to 3.
        faiss_index: The FAISS index for vector search

    Returns
    -------
        SearchResponse: Object containing search results with image data,
        similarity scores, and captions

    Raises
    ------
        HTTPException: If search index is not available or other errors occur
        during search
    """
    try:
        return await search_service.search_by_text(query, k, sort, faiss_index)
    except Exception as e:
        logger.error(f"Error in text search: {e!s}")
        raise HTTPException(status_code=500, detail=str(e)) from e
