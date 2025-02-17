from typing import Any

import faiss
import numpy as np
import pandas as pd

from multi_modal_retrival_pipeline.logging import logger


def create_faiss_index(data: pd.DataFrame) -> Any:
    """Create embeddings array and dimension for FAISS index.

    Args:
        data: DataFrame containing 'embeddings' column

    Returns:
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

        logger.info(
            f"Created FAISS index with {len(embeddings)} vectors of dimension {dimension}"
        )

        return index

    except Exception as e:
        logger.error(f"Error creating FAISS index: {e}")
        raise
