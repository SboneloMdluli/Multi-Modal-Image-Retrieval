from fastapi import Request

from app.core.logging_config import logger


async def get_faiss_index(request: Request):
    try:
        faiss_index = getattr(request.app.state, "faiss_index", None)
        logger.info("Online features loaded successfully")
        if faiss_index is None:
            msg = "FAISS index not loaded"
            raise RuntimeError(msg)
        return faiss_index
    except AttributeError:
        msg = "Application state not properly initialized"
        raise RuntimeError(msg)
