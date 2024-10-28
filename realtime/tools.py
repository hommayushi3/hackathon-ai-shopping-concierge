import re

from realtime.product_search.tools import SearchByTextQuery, SearchByImageQuery
from realtime.virtual_try_on import VirtualTryOn
from pydantic import BaseModel, Field


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


class QueryStockPrice(BaseModel):
    "Queries the latest stock price information for a given stock symbol."
    symbol: str = Field(..., description="The stock symbol to query (e.g., 'AAPL' for Apple Inc.)")
    period: str = Field(..., description="The time period for which to retrieve stock data (e.g., '1d' for one day, '1mo' for one month)")

    @staticmethod
    async def handler(symbol: str, period: str):
        try:
            test = "text"
            return test
 
        except Exception as e:
            return {"error": str(e)}

# draw_plotly_chart_def = {
#     "name": "draw_plotly_chart",
#     "description": "Draws a Plotly chart based on the provided JSON figure and displays it with an accompanying message.",
#     "parameters": {
#       "type": "object",
#       "properties": {
#         "message": {
#           "type": "string",
#           "description": "The message to display alongside the chart"
#         },
#         "plotly_json_fig": {
#           "type": "string",
#           "description": "A JSON string representing the Plotly figure to be drawn"
#         }
#       },
#       "required": ["message", "plotly_json_fig"]
#     }
# }

# async def draw_plotly_chart_handler(message: str, plotly_json_fig):
#     fig = plotly.io.from_json(plotly_json_fig)
#     elements = [cl.Plotly(name="chart", figure=fig, display="inline")]

#     await cl.Message(content=message, elements=elements).send()
    
# draw_plotly_chart = (draw_plotly_chart_def, draw_plotly_chart_handler)

tool_models = [SearchByTextQuery, SearchByImageQuery, VirtualTryOn]
tools = list(map(pydantic_to_tool_schema, tool_models))
