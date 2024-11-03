import asyncio
import os
from enum import Enum

import chainlit as cl
from io import BytesIO
from PIL import Image
from realtime.virtual_try_on_cache import RedisCache
from realtime.vision import VisionModel, image_to_data_uri
from pydantic import BaseModel


MODEL_IMAGE_PATH = "static/images/patrick_model.jpg"
SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY")
SEGMIND_API_BASE = "https://api.segmind.com/v1/virtual-try-on"
num_inference_steps: int = 30
guidance_scale: int = 2
seed: int = 0
base64: bool = False
redis_cache = RedisCache()
vision_model = VisionModel(model_name=os.getenv("OPENAI_VISION_MODEL"))


class ClothingCategory(str, Enum):
    UPPER_BODY = "Upper body"
    LOWER_BODY = "Lower body"
    DRESS = "Dress"


def resize_to_orig_size(image: bytes, size: tuple) -> bytes:
    """
    Resize an image to its original size.
    """
    img = Image.open(BytesIO(image))
    img = img.resize(size)

    buffer = BytesIO()
    img.save(buffer, "JPEG")
    return buffer.getvalue()


class VirtualTryOn(BaseModel):
    """
    Virtual Try-On tool for diffusing a product onto a user's image to visualize how it looks.
    This tool requires you to provide a brief description of the previous recommendation that the user is referencing:
    i.e. the product name, colour, location on the UI, enumeration, etc. It also requires you to infer the
    category of the product, which can be one of the following: 'Upper body', 'Lower body', or 'Dress'.
    Make sure to talk while the image is being generated to keep the user engaged.
    """
    description_of_previous_recommendation: str
    category: ClothingCategory

    @staticmethod
    async def handler(
        description_of_previous_recommendation: str,
        category: str
    ) -> dict:

        latest_products = cl.user_session.get("latest_products")
        index = await vision_model.identify_previous_recommendation(
            description=description_of_previous_recommendation,
            products=latest_products
        )
        product = latest_products[index]
        cl.user_session.set("latest_try_on_product", product)
        await asyncio.create_task(
            cl.CopilotFunction(
                name="try_on",
                args={"article_ids": [product["metadata"]["article_id"]]}
            ).acall()
        )

        cloth_image = product["metadata"]["image"]

        model_image = image_to_data_uri(MODEL_IMAGE_PATH).split(",")[1]

        data = {
            "model_image": model_image,
            "cloth_image": image_to_data_uri(cloth_image).split(",")[1],
            "category": category,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "base64": base64
        }
        if seed is not None:
            data["seed"] = seed
        headers = {'x-api-key': SEGMIND_API_KEY}
        response = redis_cache.make_cached_request(SEGMIND_API_BASE, json=data, headers=headers)

        elements = [
            cl.Image(
                name=f'Virtual Try On {product["metadata"]["prod_name"]}',
                content=resize_to_orig_size(response.content, (1191, 2014)),
                display="inline",
                size="large",
            )
        ]
        await cl.Message(content=f"Virtual Try On {product['metadata']['prod_name']}", elements=elements).send()

        return "Virtual Try-On completed successfully! Tell the user how good they look as if you can see the picture, being as specific as possible! Then, ask if they would like to buy the product."
