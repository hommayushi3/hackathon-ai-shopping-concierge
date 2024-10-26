import base64
import os
from mimetypes import guess_type
from inspect import cleandoc

from PIL import Image
from litellm import acompletion


VISION_SYSTEM_PROMPT = cleandoc("""
You are a helpful concise but comprehensive AI assistant with vision capabilities, serving as the eyes for a blind user.
Refrain from flowery language and add no extra words aside from the image description. You should be positive and complimentary.
""").strip()
VISION_USER_PROMPT = cleandoc("""
Please describe the image provided concisely in comprehensive detail.
""").strip()


class VisionModel:
    def __init__(self):
        self.client = acompletion
        self.model_name = os.getenv("OPENAI_VISION_MODEL")

    async def generate_image_description(self, image: Image.Image):
        """
        Generate a description of the image provided by the user.
        """
        result = await acompletion(
            model=self.model_name,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": VISION_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": VISION_USER_PROMPT
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": self._image_to_data_uri(image)}
                        }
                    ]
                }
            ],
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        )
        return result.choices[0].message.content
    
    def _image_to_data_uri(self, image: str) -> str:
        if image.startswith("data:image"):
            return image
        elif image.startswith("http"):
            return image
        else:
            mime = guess_type(image)[0]
            with open(image, "rb") as image_file:
                return f"data:{mime};base64," + base64.b64encode(image_file.read()).decode("utf-8")
