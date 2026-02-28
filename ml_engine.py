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
