"""
app.py — HealthAI Flask application (routes only).

All business logic is organized in separate modules:
  config.py          — Auth0, Gemini, Flask configuration
  constants.py       — Symptom categories, lifestyle options, etc.
  ml_engine.py       — ML model, symptom extraction, diagnosis
  agents.py          — Gemini enhancement agents + local report
  recommendations.py — Local recommendation database
  pdf_generator.py   — PDF report generation
"""

import io
from functools import wraps
from urllib.parse import quote_plus, urlencode

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, send_file,
)

from config import FLASK_SECRET_KEY, AUTH0_DOMAIN, AUTH0_CLIENT_ID, init_oauth
from constants import BODY_AREA_SYMPTOM_MAP
from ml_engine import (
    metadata, SYMPTOMS, extract_symptoms_from_text,
    get_related_symptoms_for_complaint, run_ml_diagnosis,
    generate_dynamic_steps,
)
from agents import (
    run_gemini_diagnosis, run_gemini_recommendations,
    run_gemini_summary, generate_local_report,
)
from recommendations import get_local_recommendations
from pdf_generator import generate_pdf_report
from config import GEMINI_AVAILABLE
from integrations import (
    speak_report, store_health_data, get_health_stats,
    upload_report_to_cloud, hash_report, store_on_blockchain,
    get_integration_status,
)

# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

oauth = init_oauth(app)


def login_required(f):
    """Decorator to require Auth0 login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes — Auth0
# ---------------------------------------------------------------------------

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/callback")
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token.get("userinfo", token)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {"returnTo": url_for("index", _external=True), "client_id": AUTH0_CLIENT_ID},
            quote_via=quote_plus,
        )
    )


# ---------------------------------------------------------------------------
# Routes — Pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

@app.route("/api/status")
def api_status():
    return jsonify({
        "gemini_available": GEMINI_AVAILABLE,
        "ml_model_loaded": metadata is not None,
        "model_accuracy": metadata.get("accuracy") if metadata else None,
        "n_diseases": metadata.get("n_diseases") if metadata else 0,
        "n_symptoms": metadata.get("n_symptoms") if metadata else 0,
        "logged_in": "user" in session,
        "integrations": get_integration_status(),
    })


@app.route("/api/symptoms")
def get_symptoms_api():
    return jsonify({"symptoms": SYMPTOMS})


# ---------------------------------------------------------------------------
# Input Validation
# ---------------------------------------------------------------------------

HEALTH_KEYWORDS = {
    "pain", "ache", "sore", "hurt", "fever", "cough", "cold", "flu",
    "headache", "stomach", "nausea", "vomit", "diarrhea", "diarrhoea",
    "rash", "itch", "burn", "bleed", "blood", "swollen", "swell",
    "dizzy", "fatigue", "tired", "weak", "breath", "chest", "heart",
    "skin", "eye", "ear", "throat", "nose", "mouth", "tongue",
    "joint", "muscle", "back", "neck", "knee", "leg", "arm", "hand",
    "foot", "feet", "head", "abdomen", "belly", "urine", "pee",
    "sleep", "insomnia", "anxiety", "stress", "depression", "mood",
    "weight", "appetite", "allergy", "sneeze", "phlegm", "mucus",
    "infection", "wound", "injury", "fracture", "cramp", "spasm",
    "numbness", "tingling", "vision", "blur", "deaf", "hearing",
    "constipation", "gas", "acidity", "ulcer", "diabetes", "sugar",
    "thyroid", "asthma", "tb", "malaria", "dengue", "typhoid",
    "jaundice", "hepatitis", "cancer", "tumor", "lump", "bump",
    "pimple", "acne", "boil", "cut", "bruise", "symptom", "disease",
    "illness", "sick", "unwell", "health", "medical", "doctor",
    "medicine", "drug", "treatment", "diagnosis", "condition",
    "sweat", "chills", "shiver", "restless", "palpitation",
}


def _is_health_related(text: str) -> tuple[bool, str]:
    """Check if text is a valid health-related complaint."""
    text = text.strip()

    if len(text) < 5:
        return False, "Please describe your health concern in more detail (at least a few words)."

    if len(text.split()) < 2:
        return False, "Please describe your symptoms in a short sentence so we can help you better."

    text_lower = text.lower()
    words = set(text_lower.replace(",", " ").replace(".", " ").split())

    # Check if any health keywords are in the input
    if words & HEALTH_KEYWORDS:
        return True, ""

    # Check via NLP symptom extraction — but filter out short / ambiguous matches
    AMBIGUOUS_SYMPTOMS = {"back pain", "cold", "gas", "back"}
    extracted = extract_symptoms_from_text(text)
    medical_matches = [s for s in extracted if s.lower() not in AMBIGUOUS_SYMPTOMS or s.lower() in text_lower]
    if len(medical_matches) >= 1:
        if len(medical_matches) == 1:
            sym = medical_matches[0].lower()
            sym_words = sym.split()
            if any(sw in words for sw in sym_words):
                return True, ""
        else:
            return True, ""

    # Strict suffix matching — only match plural/tense forms
    for word in words:
        stems = {word}
        if word.endswith("s") and len(word) > 3:
            stems.add(word[:-1])
        if word.endswith("es") and len(word) > 4:
            stems.add(word[:-2])
        if word.endswith("ing") and len(word) > 5:
            stems.add(word[:-3])
        if word.endswith("ed") and len(word) > 4:
            stems.add(word[:-2])
        if word.endswith("ness") and len(word) > 6:
            stems.add(word[:-4])
        if stems & HEALTH_KEYWORDS:
            return True, ""

    return False, "That doesn't seem to be a health-related concern. Please describe your symptoms or health issue (e.g. 'I have a persistent cough and fever')."


@app.route("/api/generate-steps", methods=["POST"])
def api_generate_steps():
    """Validate complaint, then generate dynamic follow-up steps."""
    data = request.get_json()
    complaint = data.get("complaint", "").strip()

    is_valid, error_msg = _is_health_related(complaint)
    if not is_valid:
        return jsonify({"valid": False, "error": error_msg, "steps": []})

    steps = generate_dynamic_steps(complaint)
    return jsonify({"valid": True, "steps": steps})


@app.route("/api/analyze", methods=["POST"])
@login_required
def analyze():
    """Run the full analysis pipeline on all collected step data."""
    data = request.get_json()

    all_symptoms = []
    complaint = data.get("complaint", "")
    all_symptoms.extend(extract_symptoms_from_text(complaint))

    for s in data.get("selected_symptoms", []):
        if s not in all_symptoms:
            all_symptoms.append(s)

    for field in ["other_symptoms", "other_conditions", "other_body_areas"]:
        other = data.get(field, "")
        if other:
            all_symptoms.extend(
                [s for s in extract_symptoms_from_text(other) if s not in all_symptoms]
            )

    for area in data.get("body_areas", []):
        for sym in BODY_AREA_SYMPTOM_MAP.get(area, []):
            if sym not in all_symptoms:
                all_symptoms.append(sym)

    patient_data = {
        "name": data.get("name", "Not Provided"),
        "complaint": complaint,
        "age": data.get("age", "N/A"),
        "gender": data.get("gender", "N/A"),
        "duration": data.get("duration", "N/A"),
        "severity": data.get("severity", "N/A"),
        "body_areas": data.get("body_areas", []),
        "preexisting": data.get("preexisting", []),
        "lifestyle": data.get("lifestyle", {}),
        "family_history": data.get("family_history", []),
        "all_symptoms": all_symptoms,
    }

    ml_diagnosis = run_ml_diagnosis(all_symptoms)

    gemini_diag = run_gemini_diagnosis(patient_data, ml_diagnosis)
    diagnosis = gemini_diag if gemini_diag else ml_diagnosis

    gemini_recs = run_gemini_recommendations(diagnosis)
    recommendations = gemini_recs if gemini_recs else get_local_recommendations(diagnosis)

    gemini_report = run_gemini_summary(patient_data, diagnosis, recommendations)
    report = gemini_report if gemini_report else generate_local_report(
        patient_data, diagnosis, recommendations
    )

    session["report_data"] = {
        "patient_data": patient_data,
        "diagnosis": diagnosis,
        "recommendations": recommendations,
    }
    session["last_report_text"] = report
    session.modified = True

    # Store anonymized data for analytics (Snowflake or local)
    store_health_data(patient_data, diagnosis)

    sources = []
    if metadata:
        sources.append(f"ML Model ({metadata.get('accuracy', 'N/A')}%)")
    if gemini_diag or gemini_recs or gemini_report:
        sources.append("Gemini AI")

    return jsonify({
        "report": report,
        "diagnosis": diagnosis,
        "recommendations": recommendations,
        "powered_by": " + ".join(sources) if sources else "HealthAI",
        "gemini_used": bool(gemini_diag),
    })


@app.route("/api/download-report")
@login_required
def download_report():
    """Generate and download PDF report."""
    report_data = session.get("report_data")
    if not report_data:
        return jsonify({"error": "No report available"}), 404

    pdf_bytes = generate_pdf_report(
        report_data["patient_data"],
        report_data["diagnosis"],
        report_data["recommendations"],
    )

    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    return send_file(
        buffer, as_attachment=True,
        download_name="HealthAI_Report.pdf", mimetype="application/pdf",
    )


# ---------------------------------------------------------------------------
# Routes — Integration APIs
# ---------------------------------------------------------------------------

@app.route("/api/speak-report", methods=["POST"])
@login_required
def api_speak_report():
    """Convert health report to speech using ElevenLabs."""
    report_text = session.get("last_report_text", "")
    if not report_text:
        return jsonify({"error": "No report available"}), 404

    audio_bytes = speak_report(report_text)
    if audio_bytes:
        buffer = io.BytesIO(audio_bytes)
        buffer.seek(0)
        return send_file(buffer, mimetype="audio/mpeg")
    else:
        return jsonify({"error": "Voice output not available. Add ELEVENLABS_API_KEY to .env"}), 503


@app.route("/api/health-stats")
def api_health_stats():
    """Get population health analytics from Snowflake or local data."""
    stats = get_health_stats()
    return jsonify(stats)


@app.route("/api/cloud-save", methods=["POST"])
@login_required
def api_cloud_save():
    """Upload PDF report to DigitalOcean Spaces."""
    report_data = session.get("report_data")
    if not report_data:
        return jsonify({"error": "No report available"}), 404

    pdf_bytes = generate_pdf_report(
        report_data["patient_data"],
        report_data["diagnosis"],
        report_data["recommendations"],
    )
    result = upload_report_to_cloud(pdf_bytes)
    if result:
        return jsonify({"success": True, **result})
    else:
        return jsonify({"error": "Cloud storage not available. Add DO_SPACES_KEY to .env"}), 503


@app.route("/api/blockchain-verify", methods=["POST"])
@login_required
def api_blockchain_verify():
    """Hash report and store on Solana blockchain."""
    report_data = session.get("report_data")
    report_text = session.get("last_report_text", "")
    if not report_data or not report_text:
        return jsonify({"error": "No report available"}), 404

    report_hash = hash_report(report_text, report_data["patient_data"])
    result = store_on_blockchain(report_hash)
    if result:
        return jsonify({"success": True, **result})
    else:
        return jsonify({
            "success": False,
            "report_hash": report_hash,
            "message": "Blockchain not available. Add SOLANA_PRIVATE_KEY to .env",
        })


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
