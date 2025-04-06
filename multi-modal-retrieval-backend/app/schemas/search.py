from typing import List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Schema for a single search result"""

    image_data: str
    similarity: float = Field(ge=0.0, le=1.0)
    caption: str


class SearchResponse(BaseModel):
    """Schema for search response"""

    results: List[SearchResult]
