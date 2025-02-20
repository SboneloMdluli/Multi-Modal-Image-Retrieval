from datetime import timedelta

from feast import Entity, FeatureService, FeatureView, Field
from feast.infra.offline_stores.file_source import FileSource
from feast.types import Array, Bytes, Float32, Int64, String
from feast.value_type import ValueType

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
        Field(name="image_data", dtype=Bytes),
        Field(name="embedding", dtype=Array(Float32)),
        Field(name="image_tag", dtype=String),
    ],
    source=image_data_source,
    online=True,
)

# Create a feature service
image_service = FeatureService(
    name="image_service",
    features=[image_features_view],
    description="Service for retrieving image embeddings and metadata",
    tags={"Project": "Multi Modal Image Retrieval"},
    owner="Sbonelo Mdluli",
)
