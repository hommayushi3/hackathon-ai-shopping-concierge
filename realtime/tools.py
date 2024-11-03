import re

from realtime.admin_panel import PreferencesUpdate
from realtime.product_search.tools import SearchByTextQuery, SearchByImageQuery
from realtime.virtual_try_on import VirtualTryOn


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


tool_models = [SearchByTextQuery, SearchByImageQuery, VirtualTryOn, PreferencesUpdate]
tools = list(map(pydantic_to_tool_schema, tool_models))
