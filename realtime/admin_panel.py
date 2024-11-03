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

# Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["chrome-extension://*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash-002')


class PreferencesUpdate(BaseModel):
    """
    Always use this tool in parallel along with any product search query to update the database with the user's latest details/preferences if
    you learn anything new about the user. This will help us provide better recommendations in the future.
    """
    personal_details_update: Optional[str] = None
    style_preference_update: Optional[str] = None
    color_preference_update: Optional[str] = None

    @staticmethod
    async def handler(
        personal_details_update: Optional[str] = None,
        style_preference_update: Optional[str] = None,
        color_preference_update: Optional[str] = None,
    ) -> dict:
        response = requests.post(
            "http://localhost:8081/update_preferences",
            json={
                "personal_details_update": personal_details_update,
                "style_preference_update": style_preference_update,
                "color_preference_update": color_preference_update,
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
    on the current state and the following updates:
    
    Current State:
    {current_preferences}

    Updates:
    Personal Details: {update.personal_details_update}
    Style Preferences: {update.style_preference_update}
    Color Preferences: {update.color_preference_update}
    
    Only update information relevant to e-commerce recommendations. Be as concise as possible and consolidate if possible.
    Return a JSON with the keys "personal_details", "style_preferences", and "color_preferences", each formatted as bullets.
    """)
    
    response = model.generate_content(prompt)
    start_index = response.candidates[0].content.parts[0].text.find("{")
    end_index = response.candidates[0].content.parts[0].text.rfind("}") + 1
    current_preferences = json.loads(response.candidates[0].content.parts[0].text[start_index:end_index])
    
    return JSONResponse(
        status_code=200,
        content=current_preferences
    )
