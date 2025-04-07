from kedro.pipeline import Pipeline, node, pipeline

from .nodes import generate_clip_embeddings


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=generate_clip_embeddings,
                inputs=[
                    "partitioned_images",
                    "params:image_embedding_params",
                ],
                outputs="embeddings",
                name="generate_embeddings",
            ),
        ],
    )
