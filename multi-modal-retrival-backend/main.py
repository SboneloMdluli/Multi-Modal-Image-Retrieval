from contextlib import asynccontextmanager

import faiss
import uvicorn
from app.api.v1.endpoints import query_feature_store
from app.config.settings import get_api_settings, get_model_settings
from app.core.logging_config import logger
from fastapi import FastAPI

api_settings = get_api_settings()
model_settings = get_model_settings()


def load_faiss_index():
    try:
        index_path = model_settings.faiss_index_path
        if index_path.exists():
            return faiss.read_index(str(index_path))
        logger.warning(f"Warning: FAISS index not found at {index_path}")
        return None
    except Exception as e:
        logger.error(f"Error loading FAISS index: {e}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load FAISS index before app startup
    app.state.faiss_index = load_faiss_index()
    if app.state.faiss_index is not None:
        logger.info("FAISS index loaded successfully")

    yield

    # Cleanup on shutdown
    if app.state.faiss_index is not None:
        del app.state.faiss_index
        app.state.faiss_index = None
        logger.info("FAISS index cleaned up")


app = FastAPI(
    title=api_settings.project_name,
    version=api_settings.project_version,
    description=api_settings.project_description,
    openapi_url=f"{api_settings.api_v1_str}/openapi.json",
    lifespan=lifespan,
)

app.include_router(query_feature_store.router, prefix=api_settings.api_v1_str)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to FastAPI Project"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
