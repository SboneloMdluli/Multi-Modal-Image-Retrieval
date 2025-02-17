from functools import lru_cache
from pathlib import Path

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class FeatureStoreSettings(BaseSettings):
    base_url: Path = Field(default="../multi-modal-retrival-feature-store")

    @property
    def feature_store_path(self) -> Path:
        return self.base_url

    @property
    def registry_path(self) -> Path:
        return self.feature_store_path / "registry.db"

    @property
    def online_store_path(self) -> Path:
        return self.feature_store_path / "online_store.db"

    @property
    def offline_store_path(self) -> Path:
        return self.feature_store_path / "offline_store"

    model_config = ConfigDict(
        env_prefix="FEATURE_STORE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields
    )


class ModelSettings(BaseSettings):
    ml_models_registry: Path = Field(
        default="../multi-modal-retrival-pipeline/data/06_models"
    )

    @property
    def faiss_index_path(self) -> Path:
        return self.ml_models_registry / "faiss_index.idx"

    model_config = ConfigDict(
        env_prefix="MODEL_", env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


class APISettings(BaseSettings):
    project_name: str = Field(default="Multi-Modal Image Retrieval API")
    project_version: str = Field(default="1.0.0")
    project_description: str = Field(
        default="API for retrieving similar images based on text descriptions"
    )
    api_v1_str: str = Field(default="/api/v1/features")

    model_config = ConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields
    )


@lru_cache()
def get_feature_store_settings() -> FeatureStoreSettings:
    return FeatureStoreSettings()


@lru_cache()
def get_model_settings() -> ModelSettings:
    return ModelSettings()


@lru_cache()
def get_api_settings() -> APISettings:
    return APISettings()
