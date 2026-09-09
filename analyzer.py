import os
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Load local environment if running on PC
load_dotenv()

# Read API Key securely from Streamlit Cloud Secrets or local environment
API_KEY = None
try:
    import streamlit as st
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY")

# Create Gemini client securely (No hardcoded keys)
client = genai.Client(api_key=API_KEY)

# Automatic fallback models if Google has a temporary 503 busy spike on one
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-flash-lite-latest",
]

class MedicalResponse(BaseModel):
    is_symptom_diagnosis: bool = Field(description="True if symptoms are being analyzed, False if general question")
    title_en: str = Field(description="Title or condition name in English")
    title_ta: str = Field(description="Title or condition name in Tamil (தமிழ் பெயர்)")
    confidence: str = Field(default="Informational", description="Likelihood level if symptoms, or Informational")
    main_answer: str = Field(description="Direct explanation or answer in the requested language")
    detailed_points: List[str] = Field(description="Biological causes, mechanisms, or health points in the requested language")
    triggers_or_precautions: List[str] = Field(description="Triggers, precautions, or lifestyle tips in the requested language")
    search_keyword_en: str = Field(description="Clean English search keyword for finding medical video on YouTube")
    doctor_advice_or_questions: List[str] = Field(description="Questions for doctor or general medical guidance in the requested language")
    is_emergency: bool = Field(default=False, description="True if input indicates an emergency like heart attack or stroke")
    emergency_warning: str = Field(default="", description="Urgent medical warning if emergency")

def analyze_symptoms(user_input: str, language: str = "Tamil") -> MedicalResponse:
    system_instruction = f"""
    You are an expert, compassionate clinical AI assistant.
    Analyze any symptoms, health queries, or medical questions.
    
    CRITICAL LANGUAGE INSTRUCTION:
    Respond in: {language}.
    - If language is 'Tamil', write main_answer, detailed_points, triggers_or_precautions, and doctor_advice_or_questions in clear, fluent TAMIL (தமிழ்).
    - Always provide both title_en and title_ta.
    - If user asks a general question (e.g. 'reason for headache'), explain the causes thoroughly.
    - If user says 'hi' or greets, explain how you can help.
    - If symptoms represent an emergency (chest pain, stroke symptoms, severe breathing distress), set is_emergency=True.
    - Keep tone educational and helpful.
    """

    last_error = None
    # If one model is busy (503), it automatically tries the backup models!
    for model_name in FALLBACK_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=f"User query ({language}): {user_input}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=MedicalResponse,
                    temperature=0.2,
                ),
            )
            return MedicalResponse.model_validate_json(response.text)
        except Exception as e:
            last_error = e
            continue

    # Fallback if all external model connections fail
    return MedicalResponse(
        is_symptom_diagnosis=False,
        title_en="Health Guidance",
        title_ta="மருத்துவ வழிகாட்டுதல்",
        confidence="Informational",
        main_answer=f"உங்கள் கேள்விக்கான விளக்கம்: {user_input}" if language == "Tamil" else f"Information regarding: {user_input}",
        detailed_points=["சரியான நீரேற்றம் மற்றும் ஓய்வு அவசியம்." if language == "Tamil" else "Maintain adequate hydration and rest."],
        triggers_or_precautions=["அறிகுறிகள் நீடித்தால் மருத்துவரை அணுகவும்." if language == "Tamil" else "Consult a physician if symptoms persist."],
        search_keyword_en=user_input,
        doctor_advice_or_questions=["தகுந்த மருத்துவரை ஆலோசிக்கவும்." if language == "Tamil" else "Consult a doctor for advice."],
        is_emergency=False,
        emergency_warning=""
    )
