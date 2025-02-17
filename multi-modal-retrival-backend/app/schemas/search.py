from typing import List

from pydantic import BaseModel, Field


class ImageResult(BaseModel):
    image_tag: str
    image_data: str = Field(
        description="Base64 encoded image data with data URI scheme prefix (data:image/jpeg;base64,)",
        pattern="^data:image/jpeg;base64,.+",
        examples=["data:image/jpeg;base64,/9j/4AAQSkZJRg..."],
    )


class SearchResponse(BaseModel):
    query: str = Field(description="The original search query text")
    results: List[ImageResult] = Field(
        description="List of matching images with their tags"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "suits and formal wear",
                "total_results": 2,
                "results": [
                    {
                        "image_tag": "suit_001",
                        "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                    }
                ],
            }
        }
