import base64
import io
import os
import sqlite3
from typing import Dict, List

from app.core.logging_config import logger
from app.dependencies.models import get_faiss_index
from app.schemas.search import SearchResponse
from app.services.feature_store import FeatureStoreService
from app.services.vector_store import VectorStore
from app.utils.utils import timing_decorator
from fastapi import APIRouter, Depends, HTTPException, Query
from PIL import Image

router = APIRouter(
    prefix="/features",
    tags=["features"],
    responses={404: {"description": "Not found"}},
)

feature_service = FeatureStoreService()
vector_store = VectorStore()


def save_images_from_features(features: Dict[str, List]) -> List[str]:
    """Convert binary data to images and save them"""
    saved_paths = []
    os.makedirs("output", exist_ok=True)

    for i in range(len(features["image_data"])):
        image_data = features["image_data"][i]
        image_tag = features["image_tag"][i]

        if image_data and image_tag:
            try:
                image = Image.open(io.BytesIO(image_data))
                output_path = f"output/{image_tag}.jpg"
                image.save(output_path, "JPEG")
                saved_paths.append(output_path)
                logger.info(f"Image saved as: {output_path}")
            except Exception as e:
                logger.error(f"Error saving image {image_tag}: {e}")
                continue

    return saved_paths


@router.get("/search", response_model=SearchResponse)
async def search_images(
    query: str = Query(..., description="Text query to search for similar images"),
    k: int = Query(default=3, ge=1, description="Number of results to return"),
    faiss_index=Depends(get_faiss_index),
):
    """Search for similar images based on text query"""
    try:
        logger.info(f"Received search request - Query: '{query}', K: {k}")

        if faiss_index is None:
            logger.error("FAISS index not loaded")
            raise HTTPException(status_code=500, detail="Search index not available")

        # Perform similarity search
        try:
            distances, similar_indices = vector_store.retrieve_similar_images(
                query=query, index=faiss_index, top_k=k
            )
            logger.info(f"Similarity search completed for query: {query}")
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            raise HTTPException(
                status_code=500, detail="Error performing similarity search"
            )

        # Get all available image IDs
        image_ids = [str(idx) for idx in similar_indices[0]]

        # Get features from the store
        try:
            features = feature_service.get_online_features(image_ids)
            save_images_from_features(features)
            logger.info("Features retrieved successfully")
        except Exception as e:
            logger.error(f"Error retrieving features: {e}")
            raise HTTPException(
                status_code=500, detail="Error retrieving image features"
            )

        # Process results
        results = []
        for image_tag, image_data in zip(features["image_tag"], features["image_data"]):
            if image_data and image_tag:
                try:
                    # Convert binary image data to base64
                    base64_image = base64.b64encode(image_data).decode("utf-8")
                    results.append(
                        {
                            "image_tag": image_tag,
                            "image_data": f"data:image/jpeg;base64,{base64_image}",
                        }
                    )
                    logger.info(f"Processed image: {image_tag}")
                except Exception as e:
                    logger.error(f"Error processing image {image_tag}: {e}")
                    continue

        # Ensure response_data is a valid dictionary
        response_data = dict(query=query, results=results)

        logger.info(f"Returning {len(results)} results for query: {query}")
        return response_data

    except Exception as e:
        logger.error(f"Error in search_images - Query: '{query}', Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@timing_decorator
def get_table_name():
    """Get the correct table name from the database"""
    conn = sqlite3.connect("data/online_store.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        feature_tables = [t[0] for t in tables if "features" in t[0].lower()]
        if feature_tables:
            logger.info(f"Found feature table: {feature_tables[0]}")
            return feature_tables[0]
        logger.warning("No feature tables found in database")
        return None
    finally:
        conn.close()


def list_table_columns():
    """List all tables and their column names in the database"""
    conn = sqlite3.connect("data/online_store.db")
    cursor = conn.cursor()

    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        results = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            results[table_name] = columns

        return results
    finally:
        conn.close()


if __name__ == "__main__":
    # First, check what tables exist
    logger.info("Checking database tables...")
    table_name = get_table_name()
    if table_name:
        logger.info(f"Found feature table: {table_name}")

    # Show table columns
    print("\nTable structure:")
    table_columns = list_table_columns()
    for table, columns in table_columns.items():
        print(f"\n{table}:")
        for col in columns:
            print(f"  - {col}")
