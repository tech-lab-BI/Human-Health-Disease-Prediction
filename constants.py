"""
constants.py — Symptom categories, lifestyle options, pre-existing conditions, etc.
"""

# ---------------------------------------------------------------------------
# Symptom Categories (for Step 5 dynamic checkboxes)
# ---------------------------------------------------------------------------
SYMPTOM_CATEGORIES = {
    "General": ["fatigue", "weight loss", "weight gain", "high fever", "lethargy",
                 "malaise", "sweating", "chills", "shivering", "restlessness"],
    "Head & Neurological": ["headache", "dizziness", "lack of concentration",
                            "altered sensorium", "visual disturbances", "spinning movements",
                            "loss of balance", "unsteadiness"],
    "Respiratory": ["cough", "breathlessness", "continuous sneezing", "phlegm",
                     "throat irritation", "sinus pressure", "runny nose", "congestion",
                     "mucoid sputum", "rusty sputum", "blood in sputum"],
    "Digestive": ["stomach pain", "acidity", "vomiting", "nausea", "diarrhoea",
                   "constipation", "loss of appetite", "indigestion", "abdominal pain",
                   "passage of gases", "belly pain", "distention of abdomen",
                   "pain during bowel movements", "bloody stool"],
    "Skin": ["skin rash", "itching", "nodal skin eruptions", "yellowish skin",
              "pus filled pimples", "blackheads", "scurring", "skin peeling",
              "blister", "red sore around nose", "yellow crust ooze",
              "dischromic  patches", "bruising"],
    "Musculoskeletal": ["joint pain", "muscle pain", "back pain", "neck pain",
                         "knee pain", "hip joint pain", "muscle weakness",
                         "stiff neck", "swelling joints", "movement stiffness",
                         "muscle wasting", "painful walking", "cramps"],
    "Urinary": ["burning micturition", "spotting  urination", "dark urine",
                 "yellow urine", "foul smell of urine", "continuous feel of urine",
                 "bladder discomfort", "polyuria"],
    "Cardiovascular": ["chest pain", "fast heart rate", "palpitations",
                        "prominent veins on calf", "swollen blood vessels",
                        "cold hands and feets", "swollen legs"],
    "Mental Health": ["anxiety", "mood swings", "irritability", "depression",
                       "restlessness", "lack of concentration"],
    "Eyes & Ears": ["blurred and distorted vision", "redness of eyes",
                     "watering from eyes", "sunken eyes", "pain behind the eyes",
                     "yellowing of eyes"],
}

# ---------------------------------------------------------------------------
# Pre-existing condition options (Step 7)
# ---------------------------------------------------------------------------
PREEXISTING_CONDITIONS = [
    "Diabetes", "Hypertension", "Heart Disease", "Asthma / COPD",
    "Thyroid Disorder", "Liver Disease", "Kidney Disease", "Cancer",
    "Arthritis", "HIV/AIDS", "Tuberculosis", "Epilepsy", "None"
]

# ---------------------------------------------------------------------------
# Lifestyle options (Step 8)
# ---------------------------------------------------------------------------
LIFESTYLE_OPTIONS = {
    "exercise": {
        "label": "Exercise Frequency",
        "options": ["Daily", "3-4 times/week", "Occasionally", "Rarely/Never"]
    },
    "diet": {
        "label": "Diet Quality",
        "options": ["Balanced & Healthy", "Mostly Healthy", "Average", "Mostly Junk/Fast Food"]
    },
    "sleep": {
        "label": "Sleep Quality",
        "options": ["Good (7-8 hrs)", "Average (5-6 hrs)", "Poor (< 5 hrs)", "Irregular"]
    },
    "stress": {
        "label": "Stress Level",
        "options": ["Low", "Moderate", "High", "Very High"]
    },
    "smoking": {
        "label": "Smoking",
        "options": ["Never", "Quit", "Occasionally", "Regularly"]
    },
    "alcohol": {
        "label": "Alcohol",
        "options": ["Never", "Socially", "Weekly", "Daily"]
    },
}

# ---------------------------------------------------------------------------
# Family history options (Step 9)
# ---------------------------------------------------------------------------
FAMILY_HISTORY_OPTIONS = [
    "Heart Disease", "Diabetes", "Cancer", "Hypertension",
    "Asthma", "Thyroid Disorder", "Mental Health Issues",
    "Liver Disease", "Kidney Disease", "Arthritis", "None"
]

# ---------------------------------------------------------------------------
# Body area → symptom mapping
# ---------------------------------------------------------------------------
BODY_AREA_SYMPTOM_MAP = {
    "Head": ["headache", "dizziness", "visual disturbances"],
    "Chest": ["chest pain", "breathlessness", "cough"],
    "Abdomen": ["stomach pain", "abdominal pain", "nausea"],
    "Limbs": ["joint pain", "muscle pain", "swelling joints"],
    "Skin": ["skin rash", "itching", "blister"],
    "Back": ["back pain"],
    "Throat": ["throat irritation", "cough"],
    "Eyes": ["blurred and distorted vision", "redness of eyes"],
    "Joints": ["joint pain", "swelling joints", "movement stiffness"],
    "Urinary": ["burning micturition", "dark urine"],
}
