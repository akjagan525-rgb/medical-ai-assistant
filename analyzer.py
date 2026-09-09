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

FALLBACK_MODELS = [
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
]

class UniversalResponse(BaseModel):
    title_en: str = Field(description="English title or topic")
    title_ta: str = Field(description="Tamil title or topic (தமிழ் தலைப்பு)")
    category: str = Field(description="E.g., 'Symptom Diagnosis', 'Body Science', 'Fun Fact / Curious Question', 'Diet & Lifestyle'")
    main_answer: str = Field(description="Engaging, clear, direct answer to the user's question in the requested language")
    reasons_or_points: List[str] = Field(description="3-4 bullet points explaining the biological or scientific reasons")
    fun_facts_or_tips: List[str] = Field(description="Interesting facts, precautions, or practical tips in the requested language")
    tamil_video_search: str = Field(description="Exact YouTube search query to find the best Tamil video for this exact question (e.g. 'why onions make us cry science in tamil')")
    english_video_search: str = Field(description="Exact YouTube search query for English video")
    is_emergency: bool = Field(default=False, description="True ONLY if actual emergency symptoms like heart attack or stroke appear")
    emergency_warning: str = Field(default="", description="Emergency warning if needed")

def analyze_symptoms(user_input: str, language: str = "Tamil") -> UniversalResponse:
    system_instruction = f"""
    You are a friendly, super-smart, engaging AI doctor and science explainer.
    You MUST answer ANY question the user asks, including:
    1. Serious medical symptoms (fever, chest pain, diabetes, etc.).
    2. Curious, funny, or silly body questions (e.g. 'why do we sneeze?', 'why do onions make us cry?', 'why do humans yawn?', 'what happens if I eat chalk?').
    3. Daily lifestyle, diet, or wellness questions.
    4. Casual greetings or conversational questions.

    CRITICAL RULES:
    - Never reject a question! Always explain the real biological, chemical, or physiological reason in simple, entertaining, easy-to-understand language.
    - Output language: {language}.
    - If 'Tamil', write main_answer, reasons_or_points, and fun_facts_or_tips in pure, natural, engaging TAMIL (தமிழ்).
    - Always craft an exact, high-yield YouTube search term in 'tamil_video_search' and 'english_video_search' that will pull up the exact video answering that specific question.
    """

    for model_name in FALLBACK_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"User question ({language}): {user_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=UniversalResponse,
                    temperature=0.3,
                ),
            )
            return UniversalResponse.model_validate_json(response.text)
        except Exception:
            continue

    # Fallback
    return UniversalResponse(
        title_en="Health & Science Explanation",
        title_ta="அறிவியல் & மருத்துவ விளக்கம்",
        category="General",
        main_answer=f"உங்கள் கேள்விக்கான அறிவியல் விளக்கம்: {user_input}" if language == "Tamil" else f"Explanation for: {user_input}",
        reasons_or_points=["உடலின் இயற்கையான செயல்முறைகள் இதற்கு காரணம்." if language == "Tamil" else "Natural biological processes cause this."],
        fun_facts_or_tips=["சரியான நீரேற்றம் மற்றும் ஆரோக்கியமான பழக்கங்கள் முக்கியம்." if language == "Tamil" else "Stay healthy and curious!"],
        tamil_video_search=f"{user_input} அறிவியல் விளக்கம் தமிழ்",
        english_video_search=f"{user_input} science explanation",
        is_emergency=False,
        emergency_warning=""
    )
