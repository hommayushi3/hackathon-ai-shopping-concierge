from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import google.generativeai as genai
from typing import Optional, List
import json
import os
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
    personal_details_update: Optional[List[str]] = None
    style_preference_update: Optional[List[str]] = None
    color_preference_update: Optional[List[str]] = None

# Store current preferences
current_preferences = {
    "personal_details": "Name: Patrick Tan",
    "style_preferences": "",
    "color_preferences": "Favorite: Dark Blue",
}

@app.post("/update_preferences/")
async def update_preferences(update: PreferencesUpdate):
    try:
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
        
        Only update information relevant to e-commerce recommendations. Be as concise as possible.
        Return a JSON with the keys "personal_details", "style_preferences", and "color_preferences"
        """)
        
        response = model.generate_content(prompt)
        updated_preferences = json.loads(response.candidates[0].content)
        
        return response.candidates[0].content
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
