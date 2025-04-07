from datetime import timedelta

from feast import Entity, FeatureService, FeatureView, Field, Project
from feast.infra.offline_stores.file_source import FileSource
from feast.types import Array, Bytes, Float32, Int64, String
from feast.value_type import ValueType

# Define a project for the feature repo with description
project = Project(
    name="image_feature_store",
    description=(
        "Image Feature Store for Multi-Modal Retrieval System. "
        "This Feast project manages image embeddings and features for similarity search: "
        "Stores image embeddings generated from deep learning models, "
    ),
)

# Define the data source (offline)
image_data_source = FileSource(
    path="data/image_features.pq",
    timestamp_field="event_timestamp",
)

# Single image entity
image = Entity(
    name="image_id",
    join_keys=["image_id"],
    value_type=ValueType.INT64,
    description="Unique identifier for images",
)


# Feature view
image_features_view = FeatureView(
    name="image_features",
    entities=[image],
    ttl=timedelta(days=365),
    schema=[
        Field(name="image_id", dtype=Int64),
        Field(
            name="image_data", dtype=Bytes, description="Raw image data bytes"
        ),
        Field(
            name="embedding",
            dtype=Array(Float32),
            description="Image embedding vector for similarity search",
        ),
        Field(
            name="image_tag",
            dtype=String,
            description="Tag/label associated with the image",
        ),
    ],
    source=image_data_source,
    online=True,
    tags={"domain": "computer_vision", "type": "features"},
    description="Feature view containing image data, embeddings, and tags",
)

# Create a feature service
image_service = FeatureService(
    name="image_service",
    features=[image_features_view],
    description="Service for retrieving image embeddings and metadata",
    tags={"Project": "Multi Modal Image Retrieval"},
    owner="Sbonelo Mdluli",
)
