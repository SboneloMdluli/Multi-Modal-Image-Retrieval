from app.core.logging_config import logger
from app.dependencies.models import get_faiss_index
from app.schemas.search import SearchResponse
from app.services.feast_service import FeastService
from app.services.search_service import SearchService
from fastapi import APIRouter, Depends, HTTPException, Query

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
    faiss_index=Depends(get_faiss_index),
) -> SearchResponse:
    try:
        return await search_service.search_by_text(query, k, faiss_index)
    except Exception as e:
        logger.error(f"Error in text search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
