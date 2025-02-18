import io
import logging
from collections import OrderedDict
from typing import Any, Callable

import pandas as pd
from PIL import Image
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


def image_to_bytes(image: Image.Image) -> bytes:
    """Convert PIL Image to bytes.

    Args:
        image: PIL Image object

    Returns:
        bytes: Image encoded as bytes
    """
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="jpeg")
    return img_byte_arr.getvalue()


def generate_clip_embeddings(
    partitioned_images: OrderedDict[str, Callable[[], Any]], params: dict
) -> pd.DataFrame:
    """Generate CLIP embeddings for a collection of images.

    Args:
        partitioned_images: Dictionary mapping partition IDs to load functions

    Returns:
        tuple: (list of embeddings, list of file paths)
        :param partitioned_images:
        :param params:
    """
    model = SentenceTransformer("clip-ViT-B-32")
    logger.info("Initialized CLIP model")

    embeddings = []
    file_paths = []
    data = []
    current_id = params["sequence_id"]

    logger.info(f"Starting to process {len(partitioned_images)} images")
    for partition_id, partition_load_func in partitioned_images.items():
        try:
            # Get the image data directly - this returns a PIL.Image object
            image = partition_load_func()
            file_paths.append(partition_id)

            # Generate embedding from the loaded image
            embedding = model.encode(image)
            embeddings.append(embedding)

            serialized_image = image_to_bytes(image)

            data.append(
                {
                    "image_id": current_id,
                    "embedding": embedding,
                    "image_data": serialized_image,
                    "image_tag": partition_id,
                }
            )

            current_id += 1

        except Exception as e:
            logger.error(f"Error processing image {partition_id}: {e}")
            continue

    logger.info(f"Successfully processed {len(data)} images")
    return pd.DataFrame(data)
