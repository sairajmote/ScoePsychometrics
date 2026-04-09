import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")

def get_model():
    """Tries to initialize the best available Gemini model."""
    if not api_key or api_key == "your_api_key_here":
        return None
    
    try:
        genai.configure(api_key=api_key)
        # We've verified these exact model names are available for this key
        for model_name in ["models/gemini-flash-latest", "models/gemini-2.0-flash", "models/gemini-pro-latest"]:
            try:
                # We initialize with a global safety setting to avoid false positives on psychometric terms
                m = genai.GenerativeModel(
                    model_name=model_name,
                    safety_settings={
                        "HATE": "BLOCK_NONE",
                        "HARASSMENT": "BLOCK_NONE",
                        "SEXUAL": "BLOCK_NONE",
                        "DANGEROUS": "BLOCK_NONE",
                    }
                )
                return m
            except Exception as e:
                print(f"Model Init failed for {model_name}: {e}")
                continue
        print("No valid models could be initialized.")
        return None
    except Exception as e:
        print(f"GenAI Configuration failed: {e}")
        return None

model = get_model()

def generate_ai_insights(mbti_results: Dict[str, Any], 
                         temperament_results: Dict[str, Any], 
                         enneagram_results: Dict[str, Any], 
                         big5_results: Dict[str, Any],
                         brain_dominance_results: Dict[str, Any] = None,
                         mi_results: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generates a professional psychometric overview using Gemini as a JSON object."""
    global model
    
    fallback = {
        "personality_summary": "AI Overview is currently processing. Please check back in a moment or verify your API configuration.",
        "top_strengths": ["Analytical Thinking", "Strategic Planning", "Adaptability"],
        "growth_areas": ["Communication style", "Time management"],
        "recommended_career_domains": [
            {"name": "Technology", "reason": "Strong logical-mathematical background."},
            {"name": "Research", "reason": "Detailed and analytical approach to problems."}
        ],
        "compatibility_notes": {
            "work_environment": "Quiet, structured environments.",
            "team_role": "Analyst or Researcher.",
            "leadership_style": "Leading by expertise."
        }
    }

    if not model:
        model = get_model()
        if not model:
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
    You are an expert psychometrician and master behavioral analyst. Based on the provided scores, generate a comprehensive, deep-dive personality analysis.

    CANDIDATE DATA:
    - MBTI: {mbti} ({mbti_label})
    - Temperament: {temp}
    - Enneagram: {ennea}
    - Big Five Summary: {big5}
    - Brain Dominance: {brain}
    - Top Intelligences: {mi_top}

    TASK:
    Produce a detailed, multi-paragraph narrative for the "personality_summary" section. This should be a significant deep-dive (approx. 400-600 words) that explores the complex interplay between their markers.
    
    CRITICAL FORMATTING INSTRUCTIONS:
    1. Use a multi-paragraph structure.
    2. USE NUMBERED POINTS (1., 2., 3., etc.) to break down the key analysis areas (e.g., 1. Identity & Core Drives, 2. Emotional Landscape, 3. Cognitive & Learning Style).
    3. Use double newlines (\\n\\n) for vertical spacing between paragraphs and points.
    4. Ensure the content is structured for readability.

    OUTPUT SCHEMA (RETURN ONLY VALID JSON):
    {{
        "ai_overview": "A high-level, 4-6 sentence professional introductory summary for the report cover. It should be insightful and provide a strong initial impression.",
        "personality_summary": "A comprehensive 450+ word deep-dive narrative, divided into logical sections with numbered points (1., 2., 3.). Use \\n\\n for clear vertical spacing between every paragraph and point.",
        "top_strengths": ["string", "string", "string", "string", "string"],
        "growth_areas": ["string", "string", "string", "string"],
        "recommended_career_domains": [
            {{ "name": "Domain Name", "reason": "Specific reason based on their profile." }},
            {{ "name": "Domain Name", "reason": "Specific reason based on their profile." }},
            {{ "name": "Domain Name", "reason": "Specific reason based on their profile." }},
            {{ "name": "Domain Name", "reason": "Specific reason based on their profile." }}
        ],
        "compatibility_notes": {{
            "work_environment": "Describe the ideal physical and cultural workspace in detail.",
            "team_role": "Describe their natural contribution to a team in detail.",
            "leadership_style": "Describe how they lead or manage others in detail."
        }}
    }}

    Return ONLY the raw JSON object. Do not include markdown formatting or explanations.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up potential markdown formatting if Gemini includes it
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:].strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return fallback
