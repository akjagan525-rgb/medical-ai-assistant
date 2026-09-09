import os
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Load local .env file (for local PC testing)
load_dotenv()

# Reads securely from environment / Streamlit Secrets
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

class DiseaseAnalysis(BaseModel):
    disease_name_en: str = Field(description="Medical name in English (e.g. GERD, Migraine, Type 2 Diabetes)")
    disease_name_ta: str = Field(description="Medical or common name in Tamil (தமிழ் பெயர்)")
    confidence: str = Field(description="High, Moderate, or Low")
    summary: str = Field(description="2-3 sentence overview of the condition in the requested language")
    possible_causes: List[str] = Field(description="Primary biological causes and mechanisms in the requested language")
    triggers_or_risk_factors: List[str] = Field(description="Triggers and risk factors in the requested language")
    search_keyword_en: str = Field(description="Standard English condition name for video search")
    questions_for_doctor: List[str] = Field(description="Questions to ask a doctor in the requested language")
    is_emergency: bool = Field(description="True if symptoms require immediate hospital ER care")
    emergency_warning: str = Field(default="", description="Urgent medical advice in the requested language if emergency")

def analyze_symptoms(symptoms_text: str, language: str = "Tamil") -> DiseaseAnalysis:
    system_instruction = f"""
    You are an expert clinical AI assistant for patient education.
    Analyze any symptoms provided and provide educational differential diagnoses and biological causes.
    
    CRITICAL LANGUAGE INSTRUCTION:
    The user wants the explanation in: {language}.
    - If language is 'Tamil', write the summary, causes, triggers, questions_for_doctor, and emergency_warning in clean, fluent, easy-to-understand TAMIL (தமிழ்).
    - Always provide both the English name (disease_name_en) and Tamil name (disease_name_ta).
    - If symptoms represent a life-threatening emergency (heart attack, stroke, acute severe breathing difficulty), set is_emergency to True and give an urgent warning.
    - Maintain an educational tone, clarifying this is not a substitute for a licensed doctor.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"Patient symptoms ({language}): {symptoms_text}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=DiseaseAnalysis,
            temperature=0.2,
        ),
    )
    return DiseaseAnalysis.model_validate_json(response.text)