"""
ml_engine.py — ML model loading, symptom extraction (NLP), and diagnosis.

Now supports both Random Forest and SVM models.
"""

import os
import json
import pickle
import difflib
import numpy as np

from constants import SYMPTOM_CATEGORIES

# ---------------------------------------------------------------------------
# Load ML models + metadata
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

rf_model = None
svm_model = None
label_encoder = None
metadata = None

try:
    with open(os.path.join(MODEL_DIR, "rf_disease_model.pkl"), "rb") as f:
        rf_model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "svm_disease_model.pkl"), "rb") as f:
        svm_model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
        label_encoder = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "metadata.json"), "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"✅ ML models loaded — {metadata['n_diseases']} diseases")
except Exception as e:
    print(f"❌ Could not load ML models: {e}")

SYMPTOMS = metadata["symptoms"] if metadata else []
SYMPTOM_COLUMNS = metadata["symptom_columns"] if metadata else []
DISEASES = metadata["diseases"] if metadata else []
KNOWN_DISEASES_STR = ", ".join(DISEASES) if DISEASES else "various common diseases"


# ---------------------------------------------------------------------------
# Symptom Extraction (NLP fuzzy match)
# ---------------------------------------------------------------------------

def extract_symptoms_from_text(text: str) -> list[str]:
    """Extract known symptoms from free-text using fuzzy matching."""
    text_lower = text.lower()
    found = []
    for symptom in SYMPTOMS:
        if symptom.lower() in text_lower:
            found.append(symptom)
    words = text_lower.replace(",", " ").replace(".", " ").split()
    phrases = words[:]
    for i in range(len(words) - 1):
        phrases.append(f"{words[i]} {words[i+1]}")
    for i in range(len(words) - 2):
        phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    for phrase in phrases:
        matches = difflib.get_close_matches(phrase, [s.lower() for s in SYMPTOMS], n=1, cutoff=0.7)
        if matches:
            idx = [s.lower() for s in SYMPTOMS].index(matches[0])
            if SYMPTOMS[idx] not in found:
                found.append(SYMPTOMS[idx])
    return found


def symptoms_to_vector(symptom_list: list[str]) -> np.ndarray:
    """Convert a list of symptom names to a binary feature vector."""
    vector = np.zeros(len(SYMPTOM_COLUMNS))
    symptom_lower_map = {s.lower(): i for i, s in enumerate(SYMPTOMS)}
    for symptom in symptom_list:
        idx = symptom_lower_map.get(symptom.lower())
        if idx is not None:
            vector[idx] = 1
    return vector.reshape(1, -1)


# ---------------------------------------------------------------------------
# ML Diagnosis Agent (Random Forest + SVM ensemble)
# ---------------------------------------------------------------------------

def run_ml_diagnosis(symptom_list: list[str]) -> dict:
    """Run both ML models to predict diseases and combine results."""
    if rf_model is None or svm_model is None or label_encoder is None or not symptom_list:
        return {"error": "No symptoms or models not loaded", "top_conditions": []}

    vector = symptoms_to_vector(symptom_list)

    # Random Forest predictions
    rf_probas = rf_model.predict_proba(vector)[0]
    # SVM predictions
    svm_probas = svm_model.predict_proba(vector)[0]

    # Average ensemble (can be changed to majority vote)
    avg_probas = (rf_probas + svm_probas) / 2.0
    top_indices = np.argsort(avg_probas)[::-1][:3]

    top_conditions = []
    for idx in top_indices:
        disease = label_encoder.inverse_transform([idx])[0]
        score = avg_probas[idx]
        if score < 0.01:
            continue
        confidence = "High" if score > 0.5 else "Medium" if score > 0.2 else "Low"
        top_conditions.append({
            "name": disease,
            "confidence": confidence,
            "confidence_score": round(float(score) * 100, 1),
            "reasoning": f"Ensemble (RF+SVM): {round(float(score) * 100, 1)}% probability",
        })

    return {
        "extracted_symptoms": symptom_list,
        "top_conditions": top_conditions,
        "details": {
            "RandomForest": rf_model.__class__.__name__,
            "SVM": svm_model.__class__.__name__,
        }
    }


def get_related_symptoms_for_complaint(complaint: str) -> dict:
    """Given a primary complaint, return relevant symptom categories."""
    extracted = extract_symptoms_from_text(complaint)
    complaint_lower = complaint.lower()

    scored = {}
    for cat, syms in SYMPTOM_CATEGORIES.items():
        score = 0
        for sym in syms:
            if sym.lower() in complaint_lower or any(
                difflib.get_close_matches(sym.lower(), complaint_lower.split(), n=1, cutoff=0.6)
            ):
                score += 3
            elif sym in extracted:
                score += 2
        scored[cat] = {"score": score, "symptoms": syms}

    sorted_cats = sorted(scored.items(), key=lambda x: x[1]["score"], reverse=True)
    return {cat: info["symptoms"] for cat, info in sorted_cats}


# ---------------------------------------------------------------------------
# Dynamic Step Generator
# ---------------------------------------------------------------------------

# Complaint keywords ΓåÆ relevant body areas
_KEYWORD_BODY_MAP = {
    "head": ["Head", "Eyes"], "headache": ["Head"], "migraine": ["Head"],
    "eye": ["Eyes"], "vision": ["Eyes"], "blur": ["Eyes"],
    "throat": ["Throat"], "cough": ["Throat", "Chest"], "sore throat": ["Throat"],
    "chest": ["Chest"], "breath": ["Chest"], "lung": ["Chest"],
    "stomach": ["Abdomen"], "abdomen": ["Abdomen"], "belly": ["Abdomen"],
    "nausea": ["Abdomen"], "vomit": ["Abdomen"], "diarr": ["Abdomen"],
    "back": ["Back"], "spine": ["Back"],
    "joint": ["Joints", "Limbs"], "knee": ["Joints", "Limbs"], "muscle": ["Limbs"],
    "skin": ["Skin"], "rash": ["Skin"], "itch": ["Skin"], "pimple": ["Skin"],
    "urin": ["Urinary"], "bladder": ["Urinary"],
    "fever": ["Head", "Chest"], "fatigue": ["Head", "Limbs"],
    "heart": ["Chest"], "palpitation": ["Chest"],
    "anxiety": ["Head"], "depression": ["Head"],
}

# Complaint keywords ΓåÆ relevant lifestyle factors
_KEYWORD_LIFESTYLE_MAP = {
    "stomach": ["diet", "stress"], "abdomen": ["diet", "stress"],
    "nausea": ["diet"], "vomit": ["diet"], "acidity": ["diet"],
    "fatigue": ["sleep", "exercise", "stress"], "tired": ["sleep", "exercise"],
    "headache": ["sleep", "stress", "alcohol"], "migraine": ["sleep", "stress"],
    "chest": ["smoking", "exercise"], "breath": ["smoking", "exercise"],
    "cough": ["smoking"], "lung": ["smoking"],
    "heart": ["exercise", "smoking", "stress", "diet"],
    "skin": ["diet"], "rash": ["diet"],
    "joint": ["exercise"], "muscle": ["exercise"],
    "anxiety": ["stress", "sleep"], "depression": ["stress", "sleep", "exercise"],
    "weight": ["diet", "exercise"],
    "urin": ["diet"],
    "liver": ["alcohol", "diet"],
}

# Complaint keywords ΓåÆ relevant pre-existing condition checks
_KEYWORD_CONDITION_MAP = {
    "sugar": ["Diabetes"], "thirst": ["Diabetes"],
    "breath": ["Asthma / COPD", "Heart Disease"], "chest": ["Heart Disease", "Asthma / COPD"],
    "heart": ["Heart Disease", "Hypertension"],
    "joint": ["Arthritis"], "muscle": ["Arthritis"],
    "thyroid": ["Thyroid Disorder"], "weight": ["Thyroid Disorder", "Diabetes"],
    "liver": ["Liver Disease"], "jaundice": ["Liver Disease"],
    "kidney": ["Kidney Disease"], "urin": ["Kidney Disease"],
    "cough": ["Asthma / COPD", "Tuberculosis"],
    "skin": ["Diabetes"], "fatigue": ["Diabetes", "Thyroid Disorder"],
    "bp": ["Hypertension"], "pressure": ["Hypertension"],
}

# Complaint keywords ΓåÆ relevant family history checks
_KEYWORD_FAMILY_MAP = {
    "heart": ["Heart Disease", "Hypertension"],
    "chest": ["Heart Disease"],
    "sugar": ["Diabetes"], "thirst": ["Diabetes"],
    "breath": ["Asthma"], "cough": ["Asthma"],
    "thyroid": ["Thyroid Disorder"], "weight": ["Thyroid Disorder", "Diabetes"],
    "skin": ["Diabetes"], "joint": ["Arthritis"],
    "anxiety": ["Mental Health Issues"], "depression": ["Mental Health Issues"],
    "liver": ["Liver Disease"], "kidney": ["Kidney Disease"],
    "cancer": ["Cancer"],
}

ALL_BODY_AREAS = ["Head", "Eyes", "Throat", "Chest", "Abdomen", "Back", "Limbs", "Skin", "Joints", "Urinary"]
ALL_PREEXISTING = ["Diabetes", "Hypertension", "Heart Disease", "Asthma / COPD",
                   "Thyroid Disorder", "Liver Disease", "Kidney Disease", "Cancer",
                   "Arthritis", "HIV/AIDS", "Tuberculosis", "Epilepsy", "None"]
ALL_FAMILY = ["Heart Disease", "Diabetes", "Cancer", "Hypertension", "Asthma",
              "Thyroid Disorder", "Mental Health Issues", "Liver Disease",
              "Kidney Disease", "Arthritis", "None"]
ALL_LIFESTYLE = {
    "exercise": {"label": "Exercise Frequency", "options": ["Daily", "3-4 times/week", "Occasionally", "Rarely/Never"]},
    "diet": {"label": "Diet Quality", "options": ["Balanced & Healthy", "Mostly Healthy", "Average", "Mostly Junk/Fast Food"]},
    "sleep": {"label": "Sleep Quality", "options": ["Good (7-8 hrs)", "Average (5-6 hrs)", "Poor (< 5 hrs)", "Irregular"]},
    "stress": {"label": "Stress Level", "options": ["Low", "Moderate", "High", "Very High"]},
    "smoking": {"label": "Smoking", "options": ["Never", "Quit", "Occasionally", "Regularly"]},
    "alcohol": {"label": "Alcohol", "options": ["Never", "Socially", "Weekly", "Daily"]},
}


def _match_keywords(text: str, mapping: dict) -> list:
    """Find all values from mapping whose keys appear in text."""
    text_lower = text.lower()
    found = []
    for keyword, values in mapping.items():
        if keyword in text_lower:
            for v in values:
                if v not in found:
                    found.append(v)
    return found


def generate_dynamic_steps(complaint: str) -> list[dict]:
    """
    Analyze the complaint and generate tailored follow-up step configs.
    Returns a list of step dicts with: id, title, subtitle, type, options/groups.
    """
    extracted = extract_symptoms_from_text(complaint)
    related_cats = get_related_symptoms_for_complaint(complaint)

    # Figure out which things are relevant
    relevant_body = _match_keywords(complaint, _KEYWORD_BODY_MAP)
    relevant_lifestyle = _match_keywords(complaint, _KEYWORD_LIFESTYLE_MAP)
    relevant_conditions = _match_keywords(complaint, _KEYWORD_CONDITION_MAP)
    relevant_family = _match_keywords(complaint, _KEYWORD_FAMILY_MAP)

    # Always include at least basic items
    if not relevant_body:
        relevant_body = ["Head", "Chest", "Abdomen"]
    if not relevant_lifestyle:
        relevant_lifestyle = ["sleep", "stress", "diet"]
    if not relevant_conditions:
        relevant_conditions = ["Diabetes", "Hypertension"]
    if not relevant_family:
        relevant_family = ["Heart Disease", "Diabetes"]

    # ---- Duration options: tailor based on complaint ----
    acute_keywords = ["sudden", "today", "just now", "started", "accident", "fell"]
    chronic_keywords = ["always", "long time", "months", "years", "recurring", "chronic"]
    complaint_lower = complaint.lower()

    if any(k in complaint_lower for k in acute_keywords):
        duration_options = ["Just now / a few hours", "Since today", "Since yesterday", "A few days (2-3)"]
    elif any(k in complaint_lower for k in chronic_keywords):
        duration_options = ["1-3 months", "3-6 months", "6-12 months", "More than a year", "On and off for years"]
    else:
        duration_options = ["Just today", "A few days (2-3)", "About a week", "2-3 weeks",
                           "1-3 months", "More than 3 months", "On and off"]

    # ---- Severity descriptions: tailor ----
    severity_options = [
        {"value": "Mild", "desc": "Noticeable but doesn't affect daily activities"},
        {"value": "Moderate", "desc": "Somewhat limits daily activities"},
        {"value": "Severe", "desc": "Significantly impacts daily life"},
        {"value": "Very Severe", "desc": "Debilitating, unable to perform normal activities"},
    ]

    # ---- Build the dynamic steps ----
    steps = []

    # Step 2: Age + Gender (always needed but phrased contextually)
    steps.append({
        "id": "basic_info",
        "title": "Tell us about yourself",
        "subtitle": f"To better analyze your complaint about \"{complaint[:50]}{'...' if len(complaint) > 50 else ''}\", we need some basic info.",
        "type": "mcq_group",
        "groups": [
            {"label": "Age Range", "key": "age", "input_type": "radio",
             "options": ["Under 18", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"]},
            {"label": "Gender", "key": "gender", "input_type": "radio",
             "options": ["Male", "Female", "Non-binary", "Prefer not to say"]},
        ],
    })

    # Step 3: Duration (contextual)
    steps.append({
        "id": "duration",
        "title": "How long have you had these symptoms?",
        "subtitle": "Knowing the duration helps distinguish between acute and chronic conditions.",
        "type": "radio",
        "key": "duration",
        "options": duration_options,
    })

    # Step 4: Severity
    steps.append({
        "id": "severity",
        "title": "How severe are your symptoms?",
        "subtitle": "Rate how much your symptoms are affecting your daily life right now.",
        "type": "radio_described",
        "key": "severity",
        "options": severity_options,
    })

    # Step 5: Related Symptoms (dynamic based on complaint)
    # Only show the top relevant categories (max 5) ΓÇö not all 10
    top_cats = list(related_cats.items())[:5]
    steps.append({
        "id": "symptoms",
        "title": "Are you experiencing any of these related symptoms?",
        "subtitle": f"Based on your complaint, these symptoms may be related. Auto-detected: {', '.join(extracted[:5]) if extracted else 'none yet'}.",
        "type": "checkbox_categories",
        "categories": {cat: syms for cat, syms in top_cats},
        "auto_selected": extracted,
        "has_other": True,
        "other_key": "other_symptoms",
    })

    # Step 6: Body areas (only relevant ones prioritized)
    ordered_body = relevant_body + [a for a in ALL_BODY_AREAS if a not in relevant_body]
    steps.append({
        "id": "body_areas",
        "title": "Which body areas are affected?",
        "subtitle": f"We've highlighted areas most relevant to your complaint. Select all that apply.",
        "type": "checkbox",
        "key": "body_areas",
        "options": ordered_body,
        "suggested": relevant_body,
        "has_other": True,
        "other_key": "other_body_areas",
    })

    # Step 7: Pre-existing conditions (prioritized)
    ordered_conditions = relevant_conditions + [c for c in ALL_PREEXISTING if c not in relevant_conditions]
    steps.append({
        "id": "preexisting",
        "title": "Do you have any pre-existing conditions?",
        "subtitle": f"Based on your symptoms, certain conditions are especially relevant to check.",
        "type": "checkbox",
        "key": "preexisting",
        "options": ordered_conditions,
        "suggested": relevant_conditions,
        "has_other": True,
        "other_key": "other_conditions",
    })

    # Step 8: Lifestyle (only relevant factors)
    relevant_keys = relevant_lifestyle if relevant_lifestyle else ["sleep", "stress", "diet"]
    # Always include at least 3, up to all 6
    all_keys = relevant_keys + [k for k in ALL_LIFESTYLE if k not in relevant_keys]
    lifestyle_filtered = {k: ALL_LIFESTYLE[k] for k in all_keys}
    steps.append({
        "id": "lifestyle",
        "title": "Lifestyle & Habits",
        "subtitle": f"These lifestyle factors are particularly relevant to your health concern.",
        "type": "lifestyle",
        "options": lifestyle_filtered,
    })

    # Step 9: Family history (prioritized)
    ordered_family = relevant_family + [f for f in ALL_FAMILY if f not in relevant_family]
    steps.append({
        "id": "family_history",
        "title": "Family Medical History",
        "subtitle": "Certain conditions in your family may be relevant to your symptoms.",
        "type": "checkbox",
        "key": "family_history",
        "options": ordered_family,
        "suggested": relevant_family,
        "has_other": False,
    })

    return steps
