import pytest
from kedro.pipeline import Pipeline
from multi_modal_retrival_pipeline.pipelines.data_science.pipeline import (
    create_pipeline,
)


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
    assert node.name == "create_faiss_index", "Node should have correct name"
    assert node.inputs == (["embeddings"]), "Node should have correct input"
    assert node.outputs == (["vector_store"]), "Node should have correct output"


@pytest.mark.cov
def test_pipeline_inputs_outputs():
    """Test pipeline inputs and outputs."""
    pipeline = create_pipeline()

    # Test pipeline inputs
    inputs = pipeline.inputs()
    assert len(inputs) == 1, "Pipeline should have one input"
    assert "embeddings" in inputs, "Pipeline should require embeddings as input"

    # Test pipeline outputs
    outputs = pipeline.outputs()
    assert len(outputs) == 1, "Pipeline should have one output"
    assert "vector_store" in outputs, "Pipeline should produce vector_store as output"


@pytest.mark.cov
def test_pipeline_empty_kwargs():
    """Test pipeline creation with empty kwargs."""
    pipeline = create_pipeline()
    pipeline_with_kwargs = create_pipeline(random_kwargs="test")
    assert (
        pipeline.nodes == pipeline_with_kwargs.nodes
    ), "Pipeline should be the same regardless of kwargs"
