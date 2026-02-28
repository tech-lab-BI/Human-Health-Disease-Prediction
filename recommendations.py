"""
recommendations.py — Local recommendation database for all 41 diseases.
"""

RECOMMENDATION_DB = {
    "Fungal infection": {"medicines": ["Clotrimazole cream (OTC)", "Fluconazole (Prescription)"], "home_remedies": ["Keep area dry and clean", "Apply tea tree oil"], "dietary_advice": ["Eat probiotic-rich foods", "Reduce sugar intake"], "lifestyle_changes": ["Wear breathable cotton clothes", "Avoid sharing towels"], "specialist": "Dermatologist"},
    "Allergy": {"medicines": ["Cetirizine (OTC)", "Loratadine (OTC)"], "home_remedies": ["Steam inhalation", "Saline nasal rinse"], "dietary_advice": ["Identify trigger foods", "Increase vitamin C"], "lifestyle_changes": ["Use air purifiers", "Keep windows closed during pollen season"], "specialist": "Allergist"},
    "GERD": {"medicines": ["Omeprazole (OTC)", "Ranitidine (OTC)"], "home_remedies": ["Ginger tea", "Elevate head while sleeping"], "dietary_advice": ["Avoid spicy foods", "Eat smaller meals"], "lifestyle_changes": ["Don't eat before bed", "Lose weight if overweight"], "specialist": "Gastroenterologist"},
    "Diabetes": {"medicines": ["Metformin (Prescription)", "Insulin (Prescription)"], "home_remedies": ["Bitter gourd juice", "Fenugreek seeds"], "dietary_advice": ["Low glycemic foods", "Control carbs"], "lifestyle_changes": ["Exercise 30 min daily", "Monitor blood sugar"], "specialist": "Endocrinologist"},
    "Gastroenteritis": {"medicines": ["ORS (OTC)", "Loperamide (OTC)"], "home_remedies": ["BRAT diet", "Ginger tea"], "dietary_advice": ["Avoid dairy", "Small sips of water"], "lifestyle_changes": ["Wash hands frequently", "Rest"], "specialist": "Gastroenterologist"},
    "Bronchial Asthma": {"medicines": ["Salbutamol inhaler (Prescription)", "Budesonide (Prescription)"], "home_remedies": ["Steam inhalation", "Breathing exercises"], "dietary_advice": ["Anti-inflammatory foods", "Omega-3 rich foods"], "lifestyle_changes": ["Avoid triggers", "Use air purifiers"], "specialist": "Pulmonologist"},
    "Hypertension": {"medicines": ["Amlodipine (Prescription)", "Losartan (Prescription)"], "home_remedies": ["Garlic supplements", "Deep breathing"], "dietary_advice": ["DASH diet", "Reduce sodium"], "lifestyle_changes": ["Exercise daily", "Reduce stress"], "specialist": "Cardiologist"},
    "Migraine": {"medicines": ["Sumatriptan (Prescription)", "Ibuprofen (OTC)"], "home_remedies": ["Cold compress", "Rest in dark room"], "dietary_advice": ["Avoid trigger foods", "Stay hydrated"], "lifestyle_changes": ["Regular sleep schedule", "Manage stress"], "specialist": "Neurologist"},
    "Cervical spondylosis": {"medicines": ["Ibuprofen (OTC)", "Muscle relaxants (Prescription)"], "home_remedies": ["Neck exercises", "Hot/cold compress"], "dietary_advice": ["Anti-inflammatory foods", "Calcium-rich foods"], "lifestyle_changes": ["Ergonomic workspace", "Regular stretching"], "specialist": "Orthopedic"},
    "Jaundice": {"medicines": ["Depends on cause (Prescription)"], "home_remedies": ["Sugarcane juice", "Lemon water"], "dietary_advice": ["Light meals", "Avoid fatty food"], "lifestyle_changes": ["Complete bed rest", "Avoid alcohol"], "specialist": "Hepatologist"},
    "Malaria": {"medicines": ["Chloroquine (Prescription)", "ACT (Prescription)"], "home_remedies": ["Stay hydrated", "Rest"], "dietary_advice": ["High-calorie food", "Fresh fruits"], "lifestyle_changes": ["Use mosquito nets", "Eliminate standing water"], "specialist": "Infectious Disease Specialist"},
    "Chicken pox": {"medicines": ["Acyclovir (Prescription)", "Calamine lotion (OTC)"], "home_remedies": ["Oatmeal baths", "Neem leaf bath"], "dietary_advice": ["Soft bland foods", "Stay hydrated"], "lifestyle_changes": ["Isolate to prevent spread", "Keep nails short"], "specialist": "Dermatologist"},
    "Dengue": {"medicines": ["Paracetamol only (OTC)", "IV fluids if severe (Hospital)"], "home_remedies": ["Papaya leaf extract", "Stay hydrated"], "dietary_advice": ["Coconut water", "Protein-rich diet"], "lifestyle_changes": ["Mosquito prevention", "Monitor platelet count"], "specialist": "Infectious Disease Specialist"},
    "Typhoid": {"medicines": ["Azithromycin (Prescription)", "Ciprofloxacin (Prescription)"], "home_remedies": ["Cold compress for fever", "Stay hydrated"], "dietary_advice": ["High-calorie food", "Boiled water only"], "lifestyle_changes": ["Complete rest", "Hand hygiene"], "specialist": "Infectious Disease Specialist"},
    "Hepatitis B": {"medicines": ["Tenofovir (Prescription)", "Entecavir (Prescription)"], "home_remedies": ["Milk thistle", "Rest"], "dietary_advice": ["Avoid alcohol", "Low-fat diet"], "lifestyle_changes": ["Regular liver monitoring", "Safe sex"], "specialist": "Hepatologist"},
    "Hepatitis C": {"medicines": ["Sofosbuvir + Ledipasvir (Prescription)"], "home_remedies": ["Milk thistle", "Rest"], "dietary_advice": ["No alcohol", "High-fiber diet"], "lifestyle_changes": ["Regular blood tests", "No alcohol"], "specialist": "Hepatologist"},
    "Hepatitis D": {"medicines": ["Pegylated Interferon (Prescription)"], "home_remedies": ["Rest", "Hydration"], "dietary_advice": ["Avoid alcohol", "Balanced nutrition"], "lifestyle_changes": ["Hepatitis B vaccination", "Regular monitoring"], "specialist": "Hepatologist"},
    "Hepatitis E": {"medicines": ["Supportive care -- self-limiting"], "home_remedies": ["Rest", "Stay hydrated"], "dietary_advice": ["Purified water only", "Low-fat diet"], "lifestyle_changes": ["Good sanitation", "Hand hygiene"], "specialist": "Gastroenterologist"},
    "hepatitis A": {"medicines": ["Supportive care -- self-limiting"], "home_remedies": ["Rest", "Hydration"], "dietary_advice": ["Avoid fatty foods", "Stay hydrated"], "lifestyle_changes": ["Vaccination", "Good hygiene"], "specialist": "Gastroenterologist"},
    "Alcoholic hepatitis": {"medicines": ["Prednisolone (Prescription)"], "home_remedies": ["Absolute alcohol abstinence"], "dietary_advice": ["High-protein diet", "Vitamin supplements"], "lifestyle_changes": ["Complete alcohol cessation", "Join support groups"], "specialist": "Hepatologist"},
    "Tuberculosis": {"medicines": ["RIPE regimen (Prescription -- 6-9 months)"], "home_remedies": ["Adequate nutrition", "Sunlight"], "dietary_advice": ["High-calorie, high-protein diet", "Fresh fruits"], "lifestyle_changes": ["Complete medication course", "Cover mouth when coughing"], "specialist": "Pulmonologist"},
    "Common Cold": {"medicines": ["Paracetamol (OTC)", "Decongestant (OTC)"], "home_remedies": ["Salt water gargle", "Steam inhalation", "Honey ginger tea"], "dietary_advice": ["Chicken soup", "Citrus fruits"], "lifestyle_changes": ["Rest", "Wash hands frequently"], "specialist": "General Physician"},
    "Pneumonia": {"medicines": ["Amoxicillin (Prescription)", "Azithromycin (Prescription)"], "home_remedies": ["Steam inhalation", "Warm fluids"], "dietary_advice": ["High-protein diet", "Warm soups"], "lifestyle_changes": ["Complete rest", "Deep breathing exercises"], "specialist": "Pulmonologist"},
    "Heart attack": {"medicines": ["Aspirin (emergency OTC)", "Nitroglycerin (Prescription)"], "home_remedies": ["CALL EMERGENCY IMMEDIATELY", "Chew aspirin if not allergic"], "dietary_advice": ["Low-fat, low-sodium diet", "Mediterranean diet"], "lifestyle_changes": ["Cardiac rehabilitation", "Quit smoking"], "specialist": "Cardiologist"},
    "Varicose veins": {"medicines": ["Diosmin (OTC)", "Compression stockings (OTC)"], "home_remedies": ["Elevate legs", "Cold water therapy"], "dietary_advice": ["High-fiber foods", "Reduce sodium"], "lifestyle_changes": ["Avoid prolonged standing", "Regular walking"], "specialist": "Vascular Surgeon"},
    "Hypothyroidism": {"medicines": ["Levothyroxine (Prescription)"], "home_remedies": ["Regular exercise", "Stress management"], "dietary_advice": ["Iodine-rich foods", "Selenium-rich foods"], "lifestyle_changes": ["Take medication on empty stomach", "Regular thyroid tests"], "specialist": "Endocrinologist"},
    "Hyperthyroidism": {"medicines": ["Methimazole (Prescription)", "Propranolol (Prescription)"], "home_remedies": ["Cool compresses", "Stress reduction"], "dietary_advice": ["High-calorie diet", "Limit iodine"], "lifestyle_changes": ["Regular thyroid monitoring", "Avoid caffeine"], "specialist": "Endocrinologist"},
    "Hypoglycemia": {"medicines": ["Glucose tablets (OTC)", "Glucagon kit (Prescription)"], "home_remedies": ["Eat fast-acting carbs", "Follow with protein"], "dietary_advice": ["Regular meals", "Complex carbs with protein"], "lifestyle_changes": ["Carry glucose tablets", "Monitor blood sugar"], "specialist": "Endocrinologist"},
    "Osteoarthristis": {"medicines": ["Acetaminophen (OTC)", "Glucosamine (OTC)"], "home_remedies": ["Hot/cold packs", "Gentle stretching"], "dietary_advice": ["Anti-inflammatory foods", "Omega-3 fish oil"], "lifestyle_changes": ["Low-impact exercise", "Maintain healthy weight"], "specialist": "Rheumatologist"},
    "Arthritis": {"medicines": ["NSAIDs (OTC)", "Methotrexate (Prescription)"], "home_remedies": ["Warm compresses", "Turmeric milk"], "dietary_advice": ["Anti-inflammatory diet", "Omega-3 fatty acids"], "lifestyle_changes": ["Regular gentle exercise", "Joint protection"], "specialist": "Rheumatologist"},
    "(vertigo) Paroymsal  Positional Vertigo": {"medicines": ["Meclizine (OTC)", "Betahistine (Prescription)"], "home_remedies": ["Epley maneuver", "Stay hydrated"], "dietary_advice": ["Low-sodium diet", "Avoid caffeine"], "lifestyle_changes": ["Move slowly", "Avoid sudden head movements"], "specialist": "ENT / Neurologist"},
    "Acne": {"medicines": ["Benzoyl peroxide (OTC)", "Tretinoin (Prescription)"], "home_remedies": ["Tea tree oil", "Aloe vera gel"], "dietary_advice": ["Reduce dairy and sugar", "Increase water intake"], "lifestyle_changes": ["Don't touch face", "Change pillowcases regularly"], "specialist": "Dermatologist"},
    "Urinary tract infection": {"medicines": ["Nitrofurantoin (Prescription)", "Phenazopyridine (OTC)"], "home_remedies": ["Cranberry juice", "Drink lots of water"], "dietary_advice": ["8-10 glasses of water", "Probiotic foods"], "lifestyle_changes": ["Urinate after intercourse", "Wipe front to back"], "specialist": "Urologist"},
    "Psoriasis": {"medicines": ["Topical corticosteroids (Prescription)", "Calcipotriene (Prescription)"], "home_remedies": ["Aloe vera gel", "Oatmeal baths"], "dietary_advice": ["Anti-inflammatory diet", "Omega-3 rich foods"], "lifestyle_changes": ["Moisturize daily", "Manage stress"], "specialist": "Dermatologist"},
    "Impetigo": {"medicines": ["Mupirocin ointment (Prescription)", "Cephalexin (Prescription)"], "home_remedies": ["Wash sores gently", "Don't scratch"], "dietary_advice": ["Immune-boosting foods", "Vitamin C"], "lifestyle_changes": ["Keep sores covered", "Don't share towels"], "specialist": "Dermatologist"},
    "Dimorphic hemmorhoids(piles)": {"medicines": ["Stool softeners (OTC)", "Hydrocortisone cream (OTC)"], "home_remedies": ["Sitz bath", "Witch hazel pads"], "dietary_advice": ["High-fiber diet", "8-10 glasses of water"], "lifestyle_changes": ["Don't strain", "Regular exercise"], "specialist": "Proctologist"},
    "Paralysis (brain hemorrhage)": {"medicines": ["Blood pressure management (Prescription)"], "home_remedies": ["Physiotherapy", "Speech therapy"], "dietary_advice": ["Low-sodium diet", "Brain-healthy foods"], "lifestyle_changes": ["Rehabilitation therapy", "Regular medical follow-up"], "specialist": "Neurologist"},
    "AIDS": {"medicines": ["Antiretroviral therapy / ART (Prescription)"], "home_remedies": ["Maintain hygiene", "Adequate rest"], "dietary_advice": ["High-protein diet", "Stay hydrated"], "lifestyle_changes": ["Regular check-ups", "Practice safe sex"], "specialist": "Infectious Disease Specialist"},
    "Drug Reaction": {"medicines": ["Diphenhydramine (OTC)", "Epinephrine for severe (Prescription)"], "home_remedies": ["Cool compresses", "Oatmeal baths"], "dietary_advice": ["Stay hydrated", "Eat bland foods"], "lifestyle_changes": ["Stop suspected medication", "Wear medical alert bracelet"], "specialist": "Allergist"},
    "Peptic ulcer diseae": {"medicines": ["Omeprazole (OTC)", "Sucralfate (Prescription)"], "home_remedies": ["Cabbage juice", "Probiotics"], "dietary_advice": ["Avoid spicy foods", "Small frequent meals"], "lifestyle_changes": ["Quit smoking", "Manage stress"], "specialist": "Gastroenterologist"},
    "Chronic cholestasis": {"medicines": ["Ursodeoxycholic acid (Prescription)"], "home_remedies": ["Oatmeal baths for itching", "Cool compresses"], "dietary_advice": ["Low-fat diet", "Increase fiber"], "lifestyle_changes": ["Avoid alcohol", "Regular liver tests"], "specialist": "Hepatologist"},
}


def get_local_recommendations(diagnosis: dict) -> dict:
    """Generate recommendations using the local database."""
    recs = []
    for cond in diagnosis.get("top_conditions", []):
        name = cond["name"]
        if name in RECOMMENDATION_DB:
            rec = RECOMMENDATION_DB[name].copy()
            rec["condition"] = name
            recs.append(rec)
        else:
            recs.append({
                "condition": name,
                "medicines": ["Consult a doctor"],
                "home_remedies": ["Rest and monitor"],
                "dietary_advice": ["Eat balanced meals"],
                "lifestyle_changes": ["Get adequate rest"],
                "specialist": "General Physician",
            })
    return {"recommendations": recs, "urgent_warning": None}
