import requests
import torch
from app.core.logging_config import logger
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor


class ImageService:
    # GenerativeImage2Text Transformer - using a smaller model
    model_reference = "nlpconnect/vit-gpt2-image-captioning"  # Smaller, more efficient model

    # Initialize with a flag to track if model loading succeeded
    model_loaded = False

    try:
        processor = AutoProcessor.from_pretrained(model_reference)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = AutoModelForCausalLM.from_pretrained(model_reference).to(device)
        model_loaded = True
        logger.info(f"Successfully loaded image captioning model: {model_reference}")
    except Exception as e:
        logger.error(f"Failed to load image captioning model: {str(e)}")
        processor = None
        model = None
        device = None

    def get_caption(self, image) -> str:

        try:
            inputs = ImageService.processor(images=image, return_tensors="pt").to(ImageService.device)
            with torch.no_grad():
                generated_ids = ImageService.model.generate(**inputs, max_length=20, num_beams=1, do_sample=False)

            # Decode the generated tokens
            caption = ImageService.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            logger.info(f"Caption generated successfully: {caption}")
            return caption

        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            return "Failed to generate caption"
