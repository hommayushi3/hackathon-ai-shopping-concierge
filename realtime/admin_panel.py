from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import google.generativeai as genai
from typing import Optional, List
import json
import os
import requests
from inspect import cleandoc
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel(os.getenv("OPENAI_VISION_MODEL").split("/")[-1])


class PreferencesUpdate(BaseModel):
    """
    Always use this tool in parallel along with any product search query to update the database with the user's latest details/preferences if
    you learn anything new about the user. This will help us provide better recommendations in the future.
    """
    query: str

    @staticmethod
    async def handler(
        query: str,
    ) -> dict:
        response = requests.post(
            "http://localhost:8081/update_preferences",
            json={
                "query": query
            },
            headers={"Content-Type": "application/json"},
        )
        response.json()
        return ""


# Store current preferences
current_preferences = {
    "personal_details": "- Name: Patrick Tan\n- Birthdate: 11/03",
    "style_preferences": "",
    "color_preferences": "- Favorite Color: Dark Blue",
}

@app.get("/get_preferences")
async def get_preferences():
    global current_preferences
    return JSONResponse(
        status_code=200,
        content=current_preferences
    )


@app.post("/update_preferences")
async def update_preferences(update: PreferencesUpdate):
    global current_preferences
    # try:
    # Generate updates using Gemini for any changed preferences
    prompt = cleandoc(f"""
    Please update the personal details, style preferences, and color preferences based
    on the current state and the user's most recent query:
    
    Current State:
    {current_preferences}

    Most Recent Query: {update.query}
    
    Only update information relevant to e-commerce recommendations. Be as concise as possible and consolidate if possible.
    Return a JSON with the keys "personal_details", "style_preferences", and "color_preferences", each formatted as bullets.
    Assume the user prefers the products similar to what they are searching for.
    """)
    
    response = model.generate_content(prompt)
    start_index = response.candidates[0].content.parts[0].text.find("{")
    end_index = response.candidates[0].content.parts[0].text.rfind("}") + 1
    current_preferences = json.loads(response.candidates[0].content.parts[0].text[start_index:end_index])
    print(current_preferences)
    return JSONResponse(
        status_code=200,
        content=current_preferences
    )
