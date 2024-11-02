import os
from enum import Enum

import chainlit as cl
import requests
from realtime.vision import VisionModel, image_to_data_uri
from pydantic import BaseModel


SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY")
SEGMIND_API_BASE = "https://api.segmind.com/v1/virtual-try-on"
num_inference_steps: int = 35
guidance_scale: int = 2
seed: int = None
base64: bool = False


class ClothingCategory(str, Enum):
    UPPER_BODY = "Upper body"
    LOWER_BODY = "Lower body"
    DRESS = "Dress"


class VirtualTryOn(BaseModel):
    """
    Virtual Try-On tool for diffusing a product onto a user's image to visualize how it looks.
    This tool requires you to provide a description of the previous recommendation that the user is referencing:
    i.e. the product name, colour, location on the UI, enumeration, etc. It also requires you to infer the
    category of the product, which can be one of the following: 'Upper body', 'Lower body', or 'Dress'.
    """
    description_of_previous_recommendation: str
    category: ClothingCategory

    @staticmethod
    async def handler(
        description_of_previous_recommendation: str,
        category: str
    ) -> dict:
        
        await cl.Message(content=f"Sure! Let's start up the Virtual Try-On tool for you!").send()

        vision_model = VisionModel()
        latest_products = cl.user_session.get("latest_products")
        index = await vision_model.identify_previous_recommendation(
            description=description_of_previous_recommendation,
            products=latest_products
        )
        cloth_image = latest_products[index]["metadata"]["image"]

        model_image = cl.user_session.get("latest_user_image")
        if model_image is None:
            files = None
            while not files:
                files = await cl.AskFileMessage(
                    content="Please upload a full-body image of yourself to begin virtual try-on!",
                    accept=["image/png", "image/jpeg", "image/gif"],
                    timeout=120
                ).send()
            model_image = image_to_data_uri(files[0].path).split(",")[1]
            cl.user_session.set("latest_user_image", model_image)

        await cl.Message(content=f"Generating your image now!").send()

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
        response = requests.post(SEGMIND_API_BASE, json=data, headers=headers)

        elements = [
            cl.Image(
                name=f'Virtual Try On {latest_products[index]["metadata"]["prod_name"]}',
                content=response.content,
                display="inline"
            )
        ]
        await cl.Message(content=f"Virtual Try On {latest_products[index]['metadata']['prod_name']}", elements=elements).send()

        return "Virtual Try-On completed successfully! Tell the user how good they look as if you can see the picture, being as specific as possible!"
