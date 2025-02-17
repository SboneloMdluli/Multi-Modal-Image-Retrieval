"""Pipeline construction."""
from kedro.pipeline import Pipeline

from multi_modal_retrival_pipeline.pipelines import data_processing as dp
from multi_modal_retrival_pipeline.pipelines import data_science as ds


def create_pipeline(**kwargs) -> Pipeline:
    """Create the project's pipeline.

    Returns:
        Pipeline: The pipeline object
    """
    data_processing_pipeline = dp.create_pipeline()
    data_science_pipeline = ds.create_pipeline()

    return data_processing_pipeline + data_science_pipeline
