import base64
import json
import os
import re
from inspect import cleandoc
from mimetypes import guess_type

from PIL import Image
from dotenv import load_dotenv
from litellm import acompletion
from pydantic import BaseModel

load_dotenv(override=True)


VISION_SYSTEM_PROMPT = cleandoc("""
You are a helpful concise but comprehensive AI shopping assistant for the HM store with vision capabilities, serving as the eyes for a blind user.
Refrain from flowery language and add no extra words aside from the image description. You should be positive and complimentary.
""").strip()
VISION_USER_PROMPT = cleandoc("""
Please describe the image provided concisely in comprehensive detail.
""").strip()
QUERY_PRODUCT_FILTER_PROMPT = cleandoc("""
Given the search query, filter out the 4 products below that do not match the user's preferences, and
rank the remaining products in order of relevance. Your response should be the list of indices of the
remaining relevant products in descending order of relevance. For example, [3, 1, 2], leaving out 4.
""").strip()
IMAGE_PRODUCT_FILTER_PROMPT = cleandoc("""
Given a query image of a product, filter out the {num_products} products below that are not similar to the query image, and
rank the remaining products in order of relevance. Your response should be the list of indices of the
remaining relevant products in descending order of relevance. For example, [3, 1, 2], leaving out 4.
""").strip()
METADATA_FILTER_FILTER_PROMPT = cleandoc("""
Given the search query, determine if the search filter makes sense for the query and if so, return a list
of the subset of the filter values that the user is likely to be interested in. If the search filter category
is not part of the query, return an empty list. For example, if the query is "dress" and the filter category
is "colour_group", return [].
""").strip()
IDENTIFY_PREVIOUS_RECOMMENDATION_PROMPT = cleandoc("""
Identify the index of the previous product recommendation that the user is referencing based on the description provided and the 4 products listed.
The user may reference the location of the product in the UI, here is the translation guide.
(top left = index 1, bottom left = index 2, top right = index 3, bottom right = index 4).
Your response should simply be the integer index of the product referenced, 1-{num_products}.
""").strip()


class RerankResults(BaseModel):
    indices: list[int]


class MetadataFilterResults(BaseModel):
    filter_values: list[str]


class IdentifyPreviousRecommendationIndex(BaseModel):
    index: int


SAFETY_SETTINGS = [
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


def image_to_data_uri(image: str) -> str:
    if image.startswith("data:image"):
        return image
    elif image.startswith("http"):
        return image
    else:
        mime = guess_type(image)[0]
        with open(image, "rb") as image_file:
            return f"data:{mime};base64," + base64.b64encode(image_file.read()).decode("utf-8")


class VisionModel:
    def __init__(self, model_name: str = None):
        self.client = acompletion
        self.model_name = model_name or os.getenv("OPENAI_VISION_MODEL")

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
                            "image_url": {"url": image_to_data_uri(image)}
                        }
                    ]
                }
            ],
            safety_settings=SAFETY_SETTINGS
        )
        return result.choices[0].message.content
            
    async def rerank_products_against_query(self, query: str, products: list[dict]):
        """
        Rerank products against the given query.
        """
        result = await acompletion(
            model=self.model_name,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": QUERY_PRODUCT_FILTER_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Filter and rank the products below against the query '{query}'."
                        }
                    ] + [
                        {
                            "type": "text",
                            "text": f"{i + 1}. {product['metadata']['prod_name']} - {product['metadata']['detail_desc']} ({product['metadata']['colour_group_name']} | {product['metadata']['section_name']})"
                        } if is_prod else {
                            "type": "image_url",
                            "image_url": {"url": image_to_data_uri(product['metadata']["image"])}
                        }
                        for i, product in enumerate(products)
                        for is_prod in [True, False]
                    ]
                },
            ],
            safety_settings=SAFETY_SETTINGS,
            response_format=RerankResults
        )
        return [int(i) for i in eval(result.choices[0].message.content)["indices"]]

    async def rerank_products_against_image(self, query_image: str, products: list[dict]):
        """
        Rerank products against the given query image.
        """
        result = await acompletion(
            model=self.model_name,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": IMAGE_PRODUCT_FILTER_PROMPT.format(num_products=str(len(products)))
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Filter and rank the products below against the query image."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_to_data_uri(query_image)}
                        }
                    ] + [
                        {
                            "type": "text",
                            "text": f"{i + 1}. {product['metadata']['prod_name']} - {product['metadata']['detail_desc']} ({product['metadata']['colour_group_name']} | {product['metadata']['section_name']})"
                        } if is_prod else {
                            "type": "image_url",
                            "image_url": {"url": image_to_data_uri(product["metadata"]["image"])}
                        }
                        for i, product in enumerate(products)
                        for is_prod in [True, False]
                    ]
                },
            ],
            safety_settings=SAFETY_SETTINGS,
            response_format=RerankResults
        )
        return [int(i) for i in eval(result.choices[0].message.content)["indices"]]
    
    async def identify_previous_recommendation(self, description: str, products: list[dict]):
        """
        Identify the index of the previous product recommendation that the user is referencing based on the description provided and the 4 products listed.
        """
        result = await acompletion(
            model=self.model_name,
            temperature=0,
            max_completion_tokens=10,
            messages=[
                {
                    "role": "system",
                    "content": IDENTIFY_PREVIOUS_RECOMMENDATION_PROMPT.format(num_products=str(len(products)))
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ] + [
                        {
                            "type": "text",
                            "text": f"{i + 1}. {product['metadata']['prod_name']} - {product['metadata']['detail_desc']} ({product['metadata']['colour_group_name']} | {product['metadata']['section_name']})"
                        } if is_prod else {
                            "type": "image_url",
                            "image_url": {"url": image_to_data_uri(product["metadata"]["image"])}
                        }
                        for i, product in enumerate(products)
                        for is_prod in [True, False]
                    ]
                },
            ],
            safety_settings=SAFETY_SETTINGS
        )
        try:
            return int(re.findall(r'\d', result.choices[0].message.content)[0]) - 1
        except Exception:
            return 0
        
    async def filter_metadata_filter(self, query: str, filter_category: str, filter_values: list[str]):
        """
        Filter metadata filter values based on the query.
        """
        result = await acompletion(
            model=self.model_name,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": METADATA_FILTER_FILTER_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Filter the metadata filter values for the query '{query}' and filter category '{filter_category}'.\n"
                                    f"Filter values: {str(filter_values)}"
                        }
                    ]
                },
            ],
            safety_settings=SAFETY_SETTINGS,
            response_format=MetadataFilterResults
        )
        return json.loads(result.choices[0].message.content)["filter_values"]
