"""
agents.py — Gemini-enhanced AI agents + local report generation fallback.
"""

import json

from config import gemini_model, gemini_call_safe
from ml_engine import KNOWN_DISEASES_STR, metadata


# ---------------------------------------------------------------------------
# System Prompts
# ---------------------------------------------------------------------------

DIAGNOSIS_SYSTEM_PROMPT = f"""You are DiagnosisAgent, a medical AI analyst.
You receive a patient's health data and ML predictions. Produce a JSON object (ONLY JSON, no fences):
{{"extracted_symptoms": [...], "patient_profile": {{"age": "...", "gender": "...", "location": "...", "lifestyle": "..."}},
"top_conditions": [{{"name": "Disease", "confidence": "High/Medium/Low", "reasoning": "..."}}, ...]}}
Known diseases: {KNOWN_DISEASES_STR}"""

RECOMMENDATION_SYSTEM_PROMPT = """You are RecommendationAgent. Return a JSON object (ONLY JSON, no fences):
{"recommendations": [{"condition": "Name", "medicines": ["..."], "home_remedies": ["..."], "dietary_advice": ["..."], "lifestyle_changes": ["..."], "specialist": "..."}], "urgent_warning": "... or null"}"""

SUMMARY_SYSTEM_PROMPT = """You are SummaryAgent. Compile a patient-friendly health report in Markdown with sections:
## Health Assessment Report
### Patient Summary
### Symptoms Identified
### Possible Conditions (use a table)
### You Can Use These Medicines & Treatments
### Important Warnings
### Next Steps
### Disclaimer
> AI-generated, not a substitute for professional medical advice.
Use emojis, bold text, and clear structure. Be empathetic."""


# ---------------------------------------------------------------------------
# Gemini Agent Functions
# ---------------------------------------------------------------------------

def _strip_json_fences(text: str) -> str:
    """Strip markdown code fences from JSON responses."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return text


def run_gemini_diagnosis(patient_data: dict, ml_prediction: dict):
    """Enhance ML diagnosis with Gemini. Returns dict or None."""
    def _call():
        prompt = (
            f"{DIAGNOSIS_SYSTEM_PROMPT}\n\nPatient Data:\n{json.dumps(patient_data, indent=2)}\n\n"
            f"ML Prediction:\n{json.dumps(ml_prediction, indent=2)}\n\nProduce diagnosis JSON."
        )
        resp = gemini_model.generate_content(prompt)
        return json.loads(_strip_json_fences(resp.text))

    result = gemini_call_safe(_call)
    return result if result and isinstance(result, dict) else None


def run_gemini_recommendations(diagnosis: dict):
    """Get Gemini-enhanced recommendations. Returns dict or None."""
    def _call():
        prompt = (
            f"{RECOMMENDATION_SYSTEM_PROMPT}\n\nDiagnosis:\n{json.dumps(diagnosis, indent=2)}\n\n"
            f"Produce recommendations JSON."
        )
        resp = gemini_model.generate_content(prompt)
        return json.loads(_strip_json_fences(resp.text))

    result = gemini_call_safe(_call)
    return result if result and isinstance(result, dict) else None


def run_gemini_summary(patient_data: dict, diagnosis: dict, recommendations: dict):
    """Get Gemini-enhanced summary report. Returns str or None."""
    def _call():
        prompt = (
            f"{SUMMARY_SYSTEM_PROMPT}\n\nPatient:\n{json.dumps(patient_data, indent=2)}\n\n"
            f"Diagnosis:\n{json.dumps(diagnosis, indent=2)}\n\n"
            f"Recommendations:\n{json.dumps(recommendations, indent=2)}\n\nGenerate report."
        )
        resp = gemini_model.generate_content(prompt)
        return resp.text

    return gemini_call_safe(_call)


# ---------------------------------------------------------------------------
# Local Report Generator (offline fallback)
# ---------------------------------------------------------------------------

def generate_local_report(patient_data: dict, diagnosis: dict, recommendations: dict) -> str:
    """Generate a markdown health report without Gemini."""
    r = "## Health Assessment Report\n\n"
    r += "### Patient Summary\n"
    r += f"**Patient Name:** {patient_data.get('name', 'Not Provided')}\n"
    r += f"**Age:** {patient_data.get('age', 'N/A')} | **Gender:** {patient_data.get('gender', 'N/A')}\n"
    r += f"**Primary Complaint:** {patient_data.get('complaint', 'N/A')}\n\n"

    r += "### Symptoms Identified\n"
    for s in diagnosis.get("extracted_symptoms", []):
        r += f"- {s.title()}\n"

    r += "\n### Possible Conditions\n\n| Condition | Confidence | Score |\n|-----------|-----------|-------|\n"
    for c in diagnosis.get("top_conditions", []):
        r += f"| **{c['name']}** | {c['confidence']} | {c.get('confidence_score', 'N/A')}% |\n"

    r += "\n### You Can Use These Medicines & Treatments\n\n"
    for rec in recommendations.get("recommendations", []):
        r += f"#### {rec['condition']}\n"
        r += "**You can use these medicines:** " + ", ".join(rec.get("medicines", [])) + "\n"
        r += "**Home Remedies:** " + ", ".join(rec.get("home_remedies", [])) + "\n"
        r += "**Dietary Advice:** " + ", ".join(rec.get("dietary_advice", [])) + "\n"
        r += "**Lifestyle:** " + ", ".join(rec.get("lifestyle_changes", [])) + "\n"
        r += f"**Appropriate Specialist:** {rec.get('specialist', 'General Physician')}\n\n---\n\n"

    warn = recommendations.get("urgent_warning")
    r += "### Important Warnings\n"
    r += f"**{warn}**\n\n" if warn else "No urgent warnings. Seek help if symptoms worsen.\n\n"
    r += "### Next Steps\n1. Consult the appropriate specialist\n2. Get relevant lab tests\n3. Follow up in 1-2 weeks\n\n"
    r += "### Disclaimer\n> AI-generated. Not a substitute for professional medical advice.\n\n"
    acc = metadata.get("accuracy", "N/A") if metadata else "N/A"
    r += f"*Powered by HealthAI ML Model ({acc}% accuracy)*\n"
    return r
