import io
from collections import OrderedDict

import numpy as np
import pandas as pd
import pytest
from kedro.pipeline import Pipeline
from multi_modal_retrieval_pipeline.pipelines.data_processing.nodes import (
    generate_clip_embeddings,
    image_to_bytes,
)
from multi_modal_retrieval_pipeline.pipelines.data_processing.pipeline import (
    create_pipeline,
)
from PIL import Image


@pytest.mark.cov
def test_pipeline_creation():
    """Test basic pipeline creation."""
    pipeline = create_pipeline()
    assert isinstance(pipeline, Pipeline), "Should create a Pipeline object"


@pytest.mark.cov
def test_pipeline_structure():
    """Test basic pipeline structure."""
    pipeline = create_pipeline()

    # Test number of nodes
    assert len(pipeline.nodes) == 1, "Pipeline should have exactly one node"

    # Test node properties
    node = pipeline.nodes[0]
    assert node.name == "generate_embeddings", "Node should have correct name"
    assert node.inputs == [
        "partitioned_images",
        "params:image_embedding_params",
    ], "Node should have correct input"
    assert node.outputs == ["embeddings"], "Node should have correct output"


@pytest.mark.cov
def test_pipeline_inputs_outputs():
    """Test pipeline inputs and outputs."""
    pipeline = create_pipeline()
    PIPELINE_INPUTS = 2
    PIPELINE_OUTPUTS = 1

    # Test pipeline inputs
    inputs = pipeline.inputs()
    assert len(inputs) == PIPELINE_INPUTS, "Pipeline should have two inputs"
    assert (
        "partitioned_images" in inputs
    ), "Pipeline should require partitioned_images as input"
    assert (
        "params:image_embedding_params" in inputs
    ), "Pipeline should require image_embedding_params as parameter input"

    # Test pipeline outputs
    outputs = pipeline.outputs()
    assert len(outputs) == PIPELINE_OUTPUTS, "Pipeline should have one output"
    assert "embeddings" in outputs, "Pipeline should produce embeddings as output"


@pytest.mark.cov
def test_pipeline_empty_kwargs():
    """Test pipeline creation with empty kwargs."""
    pipeline = create_pipeline()
    pipeline_with_kwargs = create_pipeline(random_kwargs="test")
    assert (
        pipeline.nodes == pipeline_with_kwargs.nodes
    ), "Pipeline should be the same regardless of kwargs"


@pytest.fixture
def sample_image():
    # Create a small test image
    img = Image.new("RGB", (100, 100), color="red")
    return img


@pytest.fixture
def sample_partitioned_images(sample_image):
    # Create a mock partitioned images dictionary
    def load_func():
        return sample_image

    return OrderedDict(
        {
            "test_image_1.jpg": load_func,
            "test_image_2.jpg": load_func,
        }
    )


def test_image_to_bytes(sample_image):
    # Test image conversion to bytes
    result = image_to_bytes(sample_image)
    assert isinstance(result, bytes)
    assert len(result) > 0

    # Verify the bytes can be converted back to an image
    img_from_bytes = Image.open(io.BytesIO(result))
    assert img_from_bytes.size == sample_image.size


def test_generate_clip_embeddings(sample_partitioned_images):
    params = {"sequence_id": 0}
    result_df = generate_clip_embeddings(sample_partitioned_images, params)

    # Check DataFrame structure
    assert isinstance(result_df, pd.DataFrame)
    assert set(result_df.columns) == {
        "image_id",
        "embedding",
        "image_data",
        "image_tag",
    }

    # Check number of processed images
    assert len(result_df) == len(sample_partitioned_images)

    # Check embeddings
    assert all(isinstance(emb, np.ndarray) for emb in result_df["embedding"])
    assert all(
        emb.shape == result_df["embedding"].iloc[0].shape
        for emb in result_df["embedding"]
    )

    # Check image data
    assert all(isinstance(img_data, bytes) for img_data in result_df["image_data"])

    # Check sequential IDs
    assert list(result_df["image_id"]) == list(range(len(sample_partitioned_images)))
