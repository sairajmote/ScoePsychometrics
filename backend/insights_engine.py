import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Configuration is loaded from system environment (Azure) or .env (Local)
load_dotenv(override=True)

# Best-to-worst order based on availability and capability.
# gemini-3.6-flash is confirmed working; others are fallbacks.
CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

def get_api_key():
    """Dynamically reads and strips the Gemini API key from environment."""
    load_dotenv(override=True)
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key if key and key != "your_api_key_here" else None

def get_client() -> genai.Client | None:
    """Returns a configured google.genai Client, or None if key is missing."""
    key = get_api_key()
    if not key:
        return None
    try:
        return genai.Client(api_key=key)
    except Exception as e:
        print(f"GenAI client creation failed: {e}")
        return None

def generate_ai_insights(mbti_results: Dict[str, Any],
                         temperament_results: Dict[str, Any],
                         enneagram_results: Dict[str, Any],
                         big5_results: Dict[str, Any],
                         brain_dominance_results: Optional[Dict[str, Any]] = None,
                         mi_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generates a professional psychometric overview using Gemini as a JSON object."""
    fallback = {
        "personality_summary": "Your AI Overview is currently processing. Please check back in a moment or verify your API configuration.",
        "top_strengths": ["Analytical Thinking", "Strategic Planning", "Adaptability"],
        "growth_areas": ["Communication style", "Time management"],
        "recommended_career_domains": [
            {"name": "Technology", "reason": "You have a strong logical-mathematical background."},
            {"name": "Research", "reason": "You take a detailed and analytical approach to problems."}
        ],
        "compatibility_notes": {
            "work_environment": "You thrive in quiet, structured environments.",
            "team_role": "You contribute best as an Analyst or Researcher.",
            "leadership_style": "You lead by expertise and precision."
        }
    }

    client = get_client()
    if not client:
        return {**fallback, "personality_summary": "Gemini API is not configured. Please add your GEMINI_API_KEY to the .env file."}

    # Extract clean strings for the prompt
    mbti = mbti_results.get("result_type", "Unknown")
    mbti_label = mbti_results.get("type_label", "Unknown Type")
    temp = temperament_results.get("temperament_type", "Unknown")
    ennea = enneagram_results.get("primary_type", {}).get("label", "Unknown")
    big5 = big5_results.get("profile_summary", "No Big Five data available.")

    brain = "Unknown"
    if brain_dominance_results:
        brain = f"{brain_dominance_results.get('dominance', {}).get('label', 'Unknown')} dominance"

    mi_top = "Unknown"
    if mi_results:
        mi_top = ", ".join(mi_results.get("dominant_labels", []))

    prompt = f"""
    Based on the provided scores, generate a comprehensive, deep-dive personality analysis for the user.

    DATA:
    - MBTI: {mbti} ({mbti_label})
    - Temperament: {temp}
    - Enneagram: {ennea}
    - Big Five Summary: {big5}
    - Brain Dominance: {brain}
    - Top Intelligences: {mi_top}

    TASK:
    Produce a detailed, multi-paragraph narrative for the "personality_summary" section. This should be a significant deep-dive (approx. 400-600 words).
    
    CRITICAL STYLE INSTRUCTIONS:
    1. ALWAYS write in the SECOND PERSON ("You", "Your"). 
    2. NEVER refer to the subject as "the candidate", "the user", or "the individual".
    3. Make the tone advisory, direct, and insightful.

    CRITICAL FORMATTING INSTRUCTIONS:
    1. Use a multi-paragraph structure.
    2. USE NUMBERED POINTS (1., 2., 3., etc.) to break down the key analysis areas (e.g., 1. Your Identity & Core Drives, 2. Your Emotional Landscape, 3. Your Natural Intelligences & Working Style).
    3. Use double newlines (\\n\\n) for vertical spacing between paragraphs and points.
    4. Ensure the content is structured for readability.

    OUTPUT SCHEMA (RETURN ONLY VALID JSON):
    {{
        "ai_overview": "A high-level, 4-6 sentence professional introductory summary for the user. Written in second person.",
        "personality_summary": "A comprehensive 450+ word deep-dive narrative, divided into logical sections with numbered points (1., 2., 3.). Written in second person. Use \\n\\n for clear vertical spacing.",
        "top_strengths": ["string", "string", "string", "string", "string"],
        "growth_areas": ["string", "string", "string", "string"],
        "recommended_career_domains": [
            {{ "name": "Domain Name", "reason": "Specific reason explaining why this suits YOU." }},
            {{ "name": "Domain Name", "reason": "Specific reason explaining why this suits YOU." }},
            {{ "name": "Domain Name", "reason": "Specific reason explaining why this suits YOU." }},
            {{ "name": "Domain Name", "reason": "Specific reason explaining why this suits YOU." }}
        ],
        "compatibility_notes": {{
            "work_environment": "Describe the ideal workspace for YOU in detail.",
            "team_role": "Describe YOUR natural contribution to a team in detail.",
            "leadership_style": "Describe how YOU lead or manage others in detail."
        }}
    }}

    Return ONLY the raw JSON object. Do not include markdown formatting or explanations.
    """

    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            print(f"Attempting AI Insights with {model_name} for MBTI: {mbti}, Temp: {temp}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    safety_settings=[
                        types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                        types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    ]
                )
            )
            text = response.text.strip()
            print(f"AI Response received from {model_name} ({len(text)} chars)")

            # Clean up potential markdown formatting if Gemini includes it
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:].strip()

            parsed_data = json.loads(text)
            print(f"AI Insights successfully parsed using {model_name}.")
            return parsed_data
        except Exception as e:
            last_error = e
            print(f"Gemini API attempt with {model_name} failed: {str(e)}")
            continue

    print(f"CRITICAL Gemini API Error across all models: {str(last_error)}")
    return fallback
