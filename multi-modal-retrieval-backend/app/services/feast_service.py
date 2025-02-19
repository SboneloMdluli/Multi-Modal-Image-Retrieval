from typing import Any, Dict, List

from app.config.settings import get_feature_store_settings
from app.core.logging_config import logger
from feast import FeatureStore


class FeastService:
    def __init__(self):
        settings = get_feature_store_settings()
        self.store = FeatureStore(str(settings.feature_store_path))

    def get_online_features(self, image_ids: List[str]) -> Dict[str, Any]:
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
            logger.error(f"Error retrieving features: {e}")
            raise
