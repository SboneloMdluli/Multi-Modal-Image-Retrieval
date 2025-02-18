from app.core.logging_config import logger
from fastapi import Request


async def get_faiss_index(request: Request):
    try:
        faiss_index = getattr(request.app.state, "faiss_index", None)
        logger.info("Online features loaded successfully")
        if faiss_index is None:
            raise RuntimeError("FAISS index not loaded")
        return faiss_index
    except AttributeError:
        raise RuntimeError("Application state not properly initialized")
