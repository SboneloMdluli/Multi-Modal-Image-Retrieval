from kedro.pipeline import Pipeline, node, pipeline

from .nodes import create_faiss_index


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=create_faiss_index,
                inputs=["embeddings"],
                outputs="vector_store",
                name="create_faiss_index",
            ),
        ]
    )
