import asyncio
import re

import chainlit as cl
from pydantic import BaseModel
from realtime.product_search.tools import SearchByTextQuery, SearchByImageQuery
from realtime.virtual_try_on import VirtualTryOn
from realtime.vision import VisionModel


vision_model = VisionModel()


def pascal_to_snake_case(s):
    # Use regex to find capital letters and add an underscore before them, except for the first letter
    snake_case = re.sub(r'(?<!^)([A-Z])', r'_\1', s).lower()
    return snake_case


def pydantic_to_tool_schema(pydantic_model):
    return (
        {
            "name": pascal_to_snake_case(pydantic_model.__name__),
            "description": pydantic_model.__doc__,
            "parameters": pydantic_model.model_json_schema()
        },
        pydantic_model.handler
    )


class AddToCart(BaseModel):
    """
    Add a particular product among the recommendations to the cart. If called right after a virtual try-on, the
    product_identifying_description should be "after_try_on". Otherwise, it should be the minimal description
    that uniquely identifies the product from the other recommendations. Always call this tool after a virtual try-on
    or if the user mentions they want to add a product to the cart.
    """
    product_identifying_description: str

    @staticmethod
    async def handler(
        product_identifying_description: str,
    ) -> dict:
        if product_identifying_description == "after_try_on":
            product = cl.user_session.get("latest_try_on_product")
        else:
            latest_products = cl.user_session.get("latest_products")
            index = await vision_model.identify_previous_recommendation(
                description=product_identifying_description,
                products=latest_products
            )
            product = latest_products[index]

        product_ids = cl.user_session.get("cart_article_ids", []) + [product["metadata"]["article_id"]]
        cl.user_session.set("cart_article_ids", product_ids)
        asyncio.create_task(
            cl.CopilotFunction(
                name="update_cart",
                args={"article_ids": product_ids}
            ).acall()
        )
        cl.Message(content=f"Added {product['metadata']['prod_name']} to cart!").send()
        
        return "Successfully added to cart!"


tool_models = [SearchByTextQuery, SearchByImageQuery, VirtualTryOn, AddToCart]
tools = list(map(pydantic_to_tool_schema, tool_models))
