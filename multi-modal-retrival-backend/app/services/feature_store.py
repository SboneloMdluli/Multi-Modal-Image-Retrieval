from typing import Any, Dict, List

from app.config.settings import get_feature_store_settings
from app.core.logging_config import logger
from app.utils.utils import timing_decorator
from feast import FeatureStore, FeatureView


class FeatureStoreService:
    def __init__(self):
        self.settings = get_feature_store_settings()
        self.store = self._init_feature_store()

    def _init_feature_store(self) -> FeatureStore:
        """Initialize the Feature Store"""
        return FeatureStore(str(self.settings.feature_store_path))

    def list_feature_views(self) -> List[FeatureView]:
        """Get all registered feature views"""
        return self.store.list_feature_views()

    @timing_decorator
    def get_online_features(self, image_ids: List[str]) -> Dict[str, Any]:
        """Get features for a list of image IDs"""
        try:
            entity_rows = [{"image_id": image_id} for image_id in image_ids]
            features = self.store.get_online_features(
                features=[
                    "image_features:image_data",
                    "image_features:image_tag",
                ],
                entity_rows=entity_rows,
            ).to_dict()
            logger.info("Online features loaded successfully")
            return features
        except Exception as e:
            logger.error(f"Error retrieving features for image_ids {image_ids}: {e}")
            raise
