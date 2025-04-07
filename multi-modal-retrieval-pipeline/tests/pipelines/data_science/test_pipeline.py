import faiss
import numpy as np
import pandas as pd
import pytest
from kedro.pipeline import Pipeline
from multi_modal_retrieval_pipeline.pipelines.data_science.nodes import (
    create_faiss_index,
)
from multi_modal_retrieval_pipeline.pipelines.data_science.pipeline import (
    create_pipeline,
)


@pytest.mark.cov()
def test_pipeline_creation() -> None:
    """Test basic pipeline creation."""
    pipeline = create_pipeline()
    assert isinstance(pipeline, Pipeline), "Should create a Pipeline object"


@pytest.mark.cov()
def test_pipeline_structure() -> None:
    """Test basic pipeline structure."""
    pipeline = create_pipeline()

    # Test number of nodes
    assert len(pipeline.nodes) == 1, "Pipeline should have exactly one node"

    # Test node properties
    node = pipeline.nodes[0]
    assert node.name == "create_faiss_index", "Node should have correct name"
    assert node.inputs == (["embeddings"]), "Node should have correct input"
    assert node.outputs == (["vector_store"]), "Node should have correct output"


def test_pipeline_inputs_outputs() -> None:
    """Test pipeline inputs and outputs."""
    pipeline = create_pipeline()

    # Test pipeline inputs
    inputs = pipeline.inputs()
    assert len(inputs) == 1, "Pipeline should have one input"
    assert "embeddings" in inputs, "Pipeline should require embeddings as input"

    # Test pipeline outputs
    outputs = pipeline.outputs()
    assert len(outputs) == 1, "Pipeline should have one output"
    assert (
        "vector_store" in outputs
    ), "Pipeline should produce vector_store as output"


@pytest.mark.cov()
def test_pipeline_empty_kwargs() -> None:
    """Test pipeline creation with empty kwargs."""
    pipeline = create_pipeline()
    pipeline_with_kwargs = create_pipeline(random_kwargs="test")
    assert (
        pipeline.nodes == pipeline_with_kwargs.nodes
    ), "Pipeline should be the same regardless of kwargs"


@pytest.fixture()
def sample_embeddings_df():
    # Create sample embeddings
    n_samples = 5
    embedding_dim = 10
    embeddings = [
        np.random.rand(embedding_dim).astype(np.float32)
        for _ in range(n_samples)
    ]

    return pd.DataFrame({"embedding": embeddings, "image_id": range(n_samples)})


def test_create_faiss_index(sample_embeddings_df) -> None:
    # Test index creation
    index = create_faiss_index(sample_embeddings_df)

    # Check if the index is of correct type
    assert isinstance(index, faiss.IndexIDMap)

    # Check if the index contains correct number of vectors
    assert index.ntotal == len(sample_embeddings_df)

    # Test search functionality
    # Create a random query vector
    query = np.random.rand(
        1,
        sample_embeddings_df["embedding"].iloc[0].shape[0],
    ).astype(np.float32)
    distance, indices = index.search(query, k=1)

    # Check if search returns expected number of results
    assert len(distance[0]) == 1
    assert 0 <= distance[0][0] < len(sample_embeddings_df)


def test_create_faiss_index_empty_df() -> None:
    # Test with empty DataFrame
    empty_df = pd.DataFrame(columns=["embedding"])

    with pytest.raises(Exception):
        create_faiss_index(empty_df)
