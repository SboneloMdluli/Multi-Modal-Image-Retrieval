from pydantic import BaseModel


class SearchResult(BaseModel):
    """Schema for a single search result."""

    image_data: str
    distance: float
    caption: str


class SearchResponse(BaseModel):
    """Schema for search response."""

    results: list[SearchResult]
