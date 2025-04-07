import logging
from typing import Any

import faiss
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def create_faiss_index(data: pd.DataFrame) -> Any:
    """Create embeddings array and dimension for FAISS index.

    Args:
    ----
        data: DataFrame containing 'embeddings' column

    Returns:
    -------
       FAISS index
    """
    logger.info("Starting to create FAISS index")

    try:
        embeddings = np.stack(data["embedding"].values)
        dimension = embeddings.shape[1]
        # Convert to float32 as required by FAISS
        embeddings = embeddings.astype(np.float32)

        index = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIDMap(index)

        # Create index
        vectors = np.array(embeddings).astype(np.float32)

        # Add vectors to the index with IDs
        index.add_with_ids(vectors, np.array(range(len(embeddings))))

        logger.info("Creating FAISS index with %d vectors", len(embeddings))

        return index

    except Exception as e:
        logger.error("Error creating FAISS index: %s", str(e))
        raise
