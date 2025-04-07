import torch
from PIL import Image
from transformers import (
    AutoTokenizer,
    VisionEncoderDecoderModel,
    ViTImageProcessor,
)


class ImageService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        # TODO : find solution to multithread with pytorch-fastapi
        torch.set_num_threads(1)  # Limit CPU threads
        model_reference = "nlpconnect/vit-gpt2-image-captioning"

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu",
        )

        self.feature_extractor = ViTImageProcessor.from_pretrained(
            model_reference,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_reference)
        self.model = VisionEncoderDecoderModel.from_pretrained(
            model_reference,
        ).to(self.device)

        # TODO : move config file
        self.max_length = 50
        self.num_beams = 4
        self.gen_kwargs = {
            "max_length": self.max_length,
            "num_beams": self.num_beams,
        }
        self._initialized = True

    def generate_caption(self, images: list[Image.Image]) -> list[str]:
        try:
            pixel_values = self.feature_extractor(
                images=images,
                return_tensors="pt",
            ).pixel_values.to(self.device)

            # Reduce memory usage
            with torch.no_grad():
                output_ids = self.model.generate(
                    pixel_values,
                    **self.gen_kwargs,
                )

            image_captions = self.tokenizer.batch_decode(
                output_ids,
                skip_special_tokens=True,
            )
            return [caption.strip() for caption in image_captions]

        except Exception as e:
            return [f"Error generating caption: {e!s}"]
        finally:
            # Clean up any CUDA memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
