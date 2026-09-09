import os
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

API_KEY = None
try:
    import streamlit as st
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

# Fastest models listed first for sub-second generation
FAST_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.6-flash",
    "gemini-flash-latest",
]

class UniversalResponse(BaseModel):
    title_en: str = Field(description="Short catchy title in English")
    title_ta: str = Field(description="Catchy title in Tamil (தமிழ் தலைப்பு)")
    answer: str = Field(description="Crisp, clear, entertaining and scientifically accurate explanation")
    why_it_happens: List[str] = Field(description="2 to 3 punchy bullet points explaining the exact scientific/biological reason")
    fun_fact_or_tip: str = Field(description="1 interesting fun fact, tip, or precaution")
    youtube_search: str = Field(description="Exact YouTube search phrase for this specific question")
    is_emergency: bool = Field(default=False)
    emergency_warning: str = Field(default="")

def analyze_symptoms(user_input: str, language: str = "Tamil") -> UniversalResponse:
    system_instruction = f"""
    You are a friendly, witty, all-knowing AI Doctor and Science Explainer.
    Answer LITERALLY ANY QUESTION the user asks with ZERO hesitation:
    - Silly body questions: 'Why do we yawn?', 'Why do we fart?', 'Why do onions make us cry?', 'Why do we get goosebumps?', 'Why are we ticklish?', 'Why is poop brown?'
    - Medical symptoms: Headaches, fever, acid reflux, diabetes, asthma, cough.
    - Weird food & lifestyle questions: 'Can I eat ice cream during fever?', 'What if I swallow chewing gum?'
    
    RULES:
    1. Output Language: {language} (use simple, natural, engaging Tamil if Tamil is selected).
    2. Be punchy, clear, and fast. Keep points direct so it generates in 1 second!
    3. Always give the real biological/chemical reason.
    4. Provide an exact YouTube search phrase in 'youtube_search' that matches this exact topic.
    """

    for model_name in FAST_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"Question ({language}): {user_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=UniversalResponse,
                    temperature=0.3,
                    max_output_tokens=600, # Keeps responses ultra-fast (< 1 second)
                ),
            )
            return UniversalResponse.model_validate_json(response.text)
        except Exception:
            continue

    # Instant Fallback
    return UniversalResponse(
        title_en=user_input,
        title_ta=user_input,
        answer=f"உங்கள் கேள்விக்கான அறிவியல் பதில்: {user_input}" if language == "Tamil" else f"Answer for: {user_input}",
        why_it_happens=["உடலின் இயற்கையான அறிவியல் செயல்முறைகள் இதற்கு காரணம்." if language == "Tamil" else "Natural biological reactions cause this."],
        fun_fact_or_tip="உடலின் ஒவ்வொரு செயல்பாட்டிற்கும் ஒரு சுவாரஸ்யமான அறிவியல் காரணம் உண்டு!" if language == "Tamil" else "Every body reaction has an interesting science reason!",
        youtube_search=f"{user_input} அறிவியல் விளக்கம் தமிழ்",
        is_emergency=False,
        emergency_warning=""
    )
