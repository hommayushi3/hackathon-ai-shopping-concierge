from typing import Dict, List

import asyncio
import aiohttp
import chainlit as cl
import requests
from realtime.product_search.base import ProductSearch, MODEL_NAME
from realtime.vision import image_to_data_uri
from pydantic import BaseModel


product_search = ProductSearch()
top_k = 4


async def async_post_aiohttp(url, data):
    requests.post(
        url,
        json=data,
        headers={"Content-Type": "application/json"},
    )


class SearchByTextQuery(BaseModel):
    """
    Search products using text query with optional metadata filters.
    """
    query: str

    @staticmethod
    async def handler(
        query: str
    ) -> List[Dict]:
        """
        Search products using text query with optional metadata filters.
        
        Args:
            query: Text search query
            filters: Dictionary of metadata filters
            top_k: Number of results to return
        """
        # Update user preferences asynchronously
        api_url = "http://localhost:8081/update_preferences"
        asyncio.create_task(async_post_aiohttp(api_url, {"query": query}))

        # Create query embedding
        query_embedding = product_search.co.embed(
            texts=[query],
            model=MODEL_NAME,
            input_type='search_query'
        ).embeddings[0]
        
        # Prepare filter conditions
        filt = await product_search.generate_filters_from_query(query)
            
        # Query the index
        results = product_search.index.query(
            vector=query_embedding,
            filter=filt,
            top_k=top_k,
            include_metadata=True
        )
        if len(results["matches"]) == 0:
            results = product_search.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
        vision_model = cl.user_session.get("vision_model")
        reranked_indices = await vision_model.rerank_products_against_query(
            query=cl.user_session.get("latest_product_image"),
            products=results["matches"]
        )
        results["matches"] = [results["matches"][i - 1] for i in reranked_indices]

        cl.user_session.set("latest_products", results["matches"])

        formatted_result = generate_product_recommendations_message(results)
        await cl.CopilotFunction(
            name="recommendations",
            args={
                "query": query,
                "filters": filt,
                "article_ids": formatted_result["article_ids"]
            }
        ).acall()
        for message in formatted_result["messages"]:
            await message.send()

        display_results = str([match["metadata"] for match in results['matches']])
        return f"Now showing recommendations for '{query}':\n{display_results}."


class SearchByImageQuery(BaseModel):
    """
    Search for products similar to a recommended product from the previous round of recommendations.
    This tool requires you to provide a description of the previous recommendation that the user is referencing:
    i.e. the product name, colour, location on the UI, enumeration, etc.
    """
    description_of_previous_recommendation: str

    @staticmethod
    async def handler(description_of_previous_recommendation: str) -> List[Dict]:
        """
        Search for similar products using the image of the latest product recommended.
        The user may reference the enumeration, location of the product in the UI, the product name, colour, etc.
        Include all relevant details in the description that might help identify which previous recommendation they
        are referencing.
        
        Args:
            user_description_of_previous_recommendation
        """
        vision_model = cl.user_session.get("vision_model")
        latest_products = cl.user_session.get("latest_products")
        product_in_question_index = await vision_model.identify_previous_recommendation(
            description=description_of_previous_recommendation,
            products=latest_products
        )
        product_in_question = latest_products[product_in_question_index]
        image = image_to_data_uri(product_in_question["metadata"]["image"])
        # Create image embedding
        print("Runing image embedding")
        query_embedding = product_search.co.embed(
            model=MODEL_NAME,
            images=[image],
            input_type='image'
        ).embeddings[0]
        print("Image embedding done")
        
        # Prepare filter conditions
        filt = await product_search.generate_filters_from_query(image)

        # Query the index
        results = product_search.index.query(
            vector=query_embedding,
            filter=filt,
            top_k=top_k,
            include_metadata=True
        )
        if len(results["matches"]) == 0:
            results = product_search.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
        reranked_indices = await vision_model.rerank_products_against_image(
            query_image=image,
            products=results["matches"]
        )
        results["matches"] = [results["matches"][i - 1] for i in reranked_indices]

        cl.user_session.set("latest_products", results["matches"])
        
        formatted_result = generate_product_recommendations_message(results)
        asyncio.create_task(cl.CopilotFunction(
            name="recommendations",
            args={
                "query": description_of_previous_recommendation,
                "filters": filt,
                "article_ids": formatted_result["article_ids"]
            }
        ).acall())
        for message in formatted_result["messages"]:
            await message.send()

        display_results = str([match["metadata"] for match in results['matches']])
        return f"Now showing similar recommendations:\n{display_results}."


def generate_product_recommendations_message(results: dict):
    messages = []
    for match in results["matches"]:
        image = cl.Image(
            name=f'{match["metadata"]["prod_name"]}',
            path=match["metadata"]["image"],
            display="inline"
        )
        messages.append(
            cl.Message(
                content=f'# {match["metadata"]["prod_name"]} ({match["metadata"]["colour_group_name"]})',
                elements=[image]
            )
        )
    return {
        "messages": messages,
        "article_ids": [match["metadata"]["article_id"] for match in results["matches"]]
    }

