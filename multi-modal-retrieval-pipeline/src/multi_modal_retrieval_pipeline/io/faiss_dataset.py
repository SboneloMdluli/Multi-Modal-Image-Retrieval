from pathlib import Path
from typing import Any, Optional

import faiss
import numpy as np
from kedro.io import AbstractDataset


class FaissDataset(AbstractDataset[tuple[np.ndarray, int], faiss.Index]):
    """``FaissDataset`` loads and saves FAISS indexes with versioning support.

    Example:
    ::
        >>> FaissDataset(
        >>>     filepath="data/04_feature/file.index",
        >>>     version=None,  # Latest version
        >>>     is_versioned=True
        >>> )
    """

    def __init__(
        self,
        filepath: str,
        version: Optional[str] = None,
        is_versioned: bool = False,
    ):
        """Creates a new instance of FaissDataset.

        Args:
            filepath: The location of the index file
            version: If specified, should be an ISO-8601 formatted timestamp
                    (YYYY-MM-DDThh.mm.ss.sssZ)
            versioned: If True, save different versions of the index
        """
        # super().__init__(PurePosixPath(filepath), version)
        self._filepath = Path(filepath)
        self._version = version
        self._versioned = is_versioned

    def _get_load_path(self) -> Path:
        """Get the full path to load the index file."""
        if not self._versioned:
            return self._filepath

        # Get all versions
        versions = self._get_versions()

        # If version is specified, use it
        if self._version:
            if self._version not in versions:
                raise ValueError(f"Version '{self._version}' not found")
            return self._get_versioned_path(self._version)

        # If no version specified, use latest
        if versions:
            latest_version = sorted(versions)[-1]
            return self._get_versioned_path(latest_version)

        raise ValueError("No versions found for versioned dataset")

    def _get_save_path(self) -> Path:
        """Get the full path to save the index file."""
        if not self._versioned:
            return self._filepath

        # Generate new version if not specified
        version = self._version or self._generate_timestamp()
        return self._get_versioned_path(version)

    def _get_versioned_path(self, version: str) -> Path:
        """Construct the full path for a specific version."""
        # Extract just the timestamp from the Version string
        if "Version" in str(version):
            # Extract the timestamp portion between single quotes
            import re

            match = re.search(r"'([^']*)'", str(version))
            if match:
                clean_version = match.group(1)
            else:
                clean_version = str(version)
        else:
            clean_version = str(version)

        version_path = Path(clean_version)
        return self._filepath.parent / version_path / self._filepath.name

    def _get_versions(self) -> list[str]:
        """List all available versions of the dataset."""
        if not self._versioned:
            return []

        try:
            base_path = self._filepath.parent
            if not base_path.exists():
                return []

            # List all directories that match ISO format
            versions = [
                d.name
                for d in base_path.iterdir()
                if d.is_dir() and self._is_valid_version(d.name)
            ]
            return sorted(versions)
        except Exception as e:
            raise ValueError(f"Error listing versions: {e}")

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if a version string is in valid ISO format."""
        try:
            from datetime import datetime

            datetime.strptime(version, "%Y-%m-%dT%H.%M.%S.%fZ")
            return True
        except ValueError:
            return False

    @staticmethod
    def _generate_timestamp() -> str:
        """Generate an ISO-8601 timestamp for versioning."""
        from datetime import datetime

        return datetime.utcnow().strftime("%Y-%m-%dT%H.%M.%S.%fZ")

    def _load(self) -> faiss.Index:
        """Loads the FAISS index.

        Returns:
            faiss.Index: Loaded FAISS index.

        Raises:
            ValueError: If the version doesn't exist or there are no versions.
        """
        load_path = self._get_load_path()
        if not load_path.exists():
            raise ValueError(f"Index file not found at {load_path}")
        return faiss.read_index(str(load_path))

    def _save(self, index: Any) -> None:
        """Saves the FAISS index.

        Args:
            index: FAISS index to save

        Raises:
            ValueError: If there's an error saving the index.
        """
        save_path = self._get_save_path()

        # Create directory if it doesn't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            faiss.write_index(index, str(save_path))
        except Exception as e:
            raise ValueError(f"Error saving index: {e}")

    def _describe(self) -> dict[str, Any]:
        """Returns a dict that describes the attributes of the dataset."""
        return {
            "filepath": self._filepath,
            "versioned": self._versioned,
            "version": self._version,
            "available_versions": self._get_versions() if self._versioned else None,
        }
