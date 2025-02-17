from pathlib import Path
from typing import Any

import faiss
import numpy as np
from kedro.io import AbstractDataset


class FaissDataset(AbstractDataset[tuple[np.ndarray, int], faiss.Index]):
    """``FaissDataset`` loads and saves FAISS indexes.

    Example:
    ::
        >>> FaissDataset(filepath="data/04_feature/embeddings.index")
    """

    def __init__(self, filepath: str):
        """Creates a new instance of FaissDataset.

        Args:
            filepath: The location of the index file.
        """
        self._filepath = Path(filepath)

    def _load(self) -> faiss.Index:
        """Loads the FAISS index.

        Returns:
            faiss.Index: Loaded FAISS index.
        """
        return faiss.read_index(str(self._filepath))

    def _save(self, index: Any) -> None:
        """Saves the FAISS index.

        Args:
            index: FAISS index
        """

        # Save the index
        faiss.write_index(index, str(self._filepath))

    def _describe(self) -> dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return {"filepath": self._filepath}
