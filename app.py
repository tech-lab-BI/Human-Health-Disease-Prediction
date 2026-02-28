from flask import Flask, render_template, request, redirect, session, url_for
import pickle
import pandas as pd
import os
import json
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode
from dotenv import load_dotenv
import google.generativeai as genai
import markdown

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key-change-in-production")

# ─── Auth0 Configuration ────────────────────────────────────────
AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID', 'placeholder')
AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET', 'placeholder')
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', 'placeholder.auth0.com')

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=f"https://{AUTH0_DOMAIN}",
    access_token_url=f"https://{AUTH0_DOMAIN}/oauth/token",
    authorize_url=f"https://{AUTH0_DOMAIN}/authorize",
    server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# ─── Gemini API Configuration ───────────────────────────────────
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ─── Load Data ──────────────────────────────────────────────────
# Load trained model
try:
    model = pickle.load(open("model.pkl", "rb"))
except:
    model = None

# Load doctors
def load_doctors():
    with open("doctors.json", "r") as f:
        return json.load(f)

# In-memory consultation requests (for hackathon demo)
consultation_requests = []

# ─── Helper: Get Gemini Remedies ────────────────────────────────
FALLBACK_REMEDIES = {
    "Fungal Infection": "<h3>About</h3><p>A fungal infection is caused by fungi that can affect skin, nails, or internal organs.</p><h3>Remedies</h3><ul><li>Keep the affected area clean and dry</li><li>Apply antifungal cream (clotrimazole/miconazole)</li><li>Wear loose, breathable clothing</li><li>Use antifungal powder in skin folds</li></ul><h3>Precautions</h3><ul><li>Avoid sharing towels or personal items</li><li>Change socks and underwear daily</li><li>Avoid walking barefoot in public showers</li></ul><h3>Diet</h3><ul><li>Eat probiotic-rich foods (yogurt, kefir)</li><li>Reduce sugar intake</li><li>Include garlic and turmeric in your diet</li></ul>",
    "Allergy": "<h3>About</h3><p>An allergy is an immune system response to a foreign substance that isn't typically harmful.</p><h3>Remedies</h3><ul><li>Identify and avoid allergens</li><li>Use antihistamines as directed</li><li>Apply cold compress for skin reactions</li><li>Use saline nasal spray for nasal symptoms</li></ul><h3>Precautions</h3><ul><li>Keep windows closed during high pollen seasons</li><li>Wash bedding frequently in hot water</li><li>Use air purifiers indoors</li></ul><h3>Diet</h3><ul><li>Eat anti-inflammatory foods (berries, leafy greens)</li><li>Include omega-3 rich foods (fish, flaxseeds)</li><li>Stay well hydrated</li></ul>",
    "Migraine": "<h3>About</h3><p>A migraine is a severe, recurring headache often accompanied by nausea and sensitivity to light.</p><h3>Remedies</h3><ul><li>Rest in a dark, quiet room</li><li>Apply cold or warm compress to your head</li><li>Stay hydrated</li><li>Practice relaxation techniques</li></ul><h3>Precautions</h3><ul><li>Maintain a regular sleep schedule</li><li>Avoid known triggers (stress, certain foods)</li><li>Limit screen time</li></ul><h3>Diet</h3><ul><li>Eat magnesium-rich foods (spinach, almonds)</li><li>Avoid processed foods and alcohol</li><li>Keep a food diary to identify triggers</li></ul>",
    "Gastritis": "<h3>About</h3><p>Gastritis is inflammation of the stomach lining, causing pain, nausea, and indigestion.</p><h3>Remedies</h3><ul><li>Eat smaller, more frequent meals</li><li>Avoid spicy and acidic foods</li><li>Try ginger or chamomile tea</li><li>Take antacids if recommended by doctor</li></ul><h3>Precautions</h3><ul><li>Avoid NSAIDs (ibuprofen, aspirin)</li><li>Limit alcohol and caffeine</li><li>Don't eat right before bed</li></ul><h3>Diet</h3><ul><li>Eat bland foods (rice, bananas, toast)</li><li>Include probiotics</li><li>Avoid fried and fatty foods</li></ul>",
    "Arthritis": "<h3>About</h3><p>Arthritis causes joint inflammation leading to pain, stiffness, and reduced mobility.</p><h3>Remedies</h3><ul><li>Apply hot/cold therapy to affected joints</li><li>Do gentle exercises (swimming, yoga)</li><li>Maintain a healthy weight</li><li>Use joint supports or braces</li></ul><h3>Precautions</h3><ul><li>Avoid high-impact activities</li><li>Don't ignore persistent joint pain</li><li>Protect joints during physical activity</li></ul><h3>Diet</h3><ul><li>Eat omega-3 rich foods (salmon, walnuts)</li><li>Include turmeric and ginger</li><li>Avoid sugar and processed foods</li></ul>",
}
DEFAULT_FALLBACK = "<h3>General Health Tips</h3><ul><li>Stay hydrated — drink at least 8 glasses of water daily</li><li>Get adequate rest and sleep (7-8 hours)</li><li>Eat a balanced diet rich in fruits and vegetables</li><li>Exercise regularly (at least 30 min/day)</li><li>Manage stress through meditation or yoga</li><li>Monitor your symptoms and keep a health diary</li></ul><h3>⚠️ Important</h3><p>Please consult a qualified healthcare professional for a proper diagnosis and personalized treatment plan.</p>"

def get_gemini_remedies(disease, symptoms):
    """Get detailed remedies from Gemini API with fallback."""
    models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash']

    for model_name in models_to_try:
        try:
            gemini_model = genai.GenerativeModel(model_name)
            prompt = f"""You are a medical health advisor AI. A patient has been predicted to possibly have: **{disease}**.
Their symptoms are: {', '.join([s for s in symptoms if s])}.

Please provide:
1. **About the Disease** - A brief explanation of what this disease is.
2. **Recommended Remedies** - Home remedies and lifestyle changes.
3. **Precautions** - Things the patient should avoid.
4. **When to See a Doctor** - Warning signs that need immediate medical attention.
5. **Dietary Suggestions** - Foods to eat and avoid.

Keep the response concise, well-formatted with bullet points, and easy to understand.
Important: This is for informational purposes only and not a substitute for professional medical advice."""

            response = gemini_model.generate_content(prompt)
            html_content = markdown.markdown(response.text)
            return html_content
        except Exception:
            continue

    # All API calls failed — use static fallback
    return FALLBACK_REMEDIES.get(disease, DEFAULT_FALLBACK)

# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

# ─── Home Page ──────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template("index.html", session=session)

# ─── Disease Prediction ────────────────────────────────────────
@app.route('/predict', methods=['POST'])
def predict():
    symptoms = [
        request.form.get('symptom1', ''),
        request.form.get('symptom2', ''),
        request.form.get('symptom3', ''),
        request.form.get('symptom4', ''),
        request.form.get('symptom5', '')
    ]
    # Filter out empty symptoms
    active_symptoms = [s for s in symptoms if s.strip()]

    # Dummy Prediction (Replace with real ML prediction)
    if "itching" in active_symptoms:
        disease = "Fungal Infection"
    elif "nodal_skin_eruptions" in active_symptoms:
        disease = "Allergy"
    elif "headache" in active_symptoms:
        disease = "Migraine"
    elif "stomach_pain" in active_symptoms:
        disease = "Gastritis"
    elif "joint_pain" in active_symptoms:
        disease = "Arthritis"
    else:
        disease = "Cervical Spondylosis"

    # Store disease in session for later use
    session['last_disease'] = disease
    session['last_symptoms'] = active_symptoms

    # Generate remedies based on login status
    remedies = ""
    if session.get('user'):
        # Logged-in user: full Gemini AI remedies
        remedies = get_gemini_remedies(disease, active_symptoms)
    # Guest users get static tips from the template

    return render_template("result.html", disease=disease, remedies=remedies, session=session)

# ─── Doctor Page ────────────────────────────────────────────────
@app.route('/doctor')
def doctor():
    return render_template("doctor.html", session=session)

# ─── Consult a Doctor (Logged-in users only) ───────────────────
@app.route('/consult')
def consult():
    if not session.get('user'):
        return redirect('/login')

    disease = request.args.get('disease', session.get('last_disease', 'Unknown'))
    doctors = load_doctors()
    return render_template("consult.html", disease=disease, doctors=doctors, session=session)

# ─── Payment Page ──────────────────────────────────────────────
@app.route('/payment')
def payment():
    if not session.get('user'):
        return redirect('/login')

    doctor_id = int(request.args.get('doctor_id', 0))
    disease = request.args.get('disease', 'Unknown')
    doctors = load_doctors()
    doctor_data = next((d for d in doctors if d['id'] == doctor_id), None)

    if not doctor_data:
        return redirect('/')

    return render_template("payment.html", doctor=doctor_data, disease=disease, session=session)

# ─── Book Consultation ─────────────────────────────────────────
@app.route('/book', methods=['POST'])
def book():
    if not session.get('user'):
        return redirect('/login')

    doctor_id = int(request.form.get('doctor_id', 0))
    disease = request.form.get('disease', 'Unknown')
    doctors = load_doctors()
    doctor_data = next((d for d in doctors if d['id'] == doctor_id), None)

    if not doctor_data:
        return redirect('/')

    # Store consultation request
    user_info = session.get('user', {}).get('userinfo', {})
    consultation = {
        'patient_name': user_info.get('name', 'Anonymous'),
        'patient_email': user_info.get('email', ''),
        'disease': disease,
        'symptoms': session.get('last_symptoms', []),
        'doctor_id': doctor_id,
        'doctor_name': doctor_data['name'],
        'amount_paid': doctor_data['fee'] + 49,
        'status': 'confirmed',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    consultation_requests.append(consultation)

    return render_template("booking_confirmed.html", doctor=doctor_data, disease=disease, session=session)

# ═══════════════════════════════════════════════════════════════
# DOCTOR PORTAL ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/doctor-login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        doctors = load_doctors()
        doctor_data = next((d for d in doctors if d['email'] == email and d['password'] == password), None)

        if doctor_data:
            session['doctor'] = doctor_data
            return redirect('/doctor-dashboard')
        else:
            return render_template("doctor_login.html", error="Invalid email or password.")

    return render_template("doctor_login.html")

@app.route('/doctor-dashboard')
def doctor_dashboard():
    if not session.get('doctor'):
        return redirect('/doctor-login')

    doctor_data = session['doctor']
    # Filter consultation requests for this doctor
    requests_list = [r for r in consultation_requests if r['doctor_id'] == doctor_data['id']]

    return render_template("doctor_dashboard.html", doctor=doctor_data, requests_list=requests_list)

@app.route('/doctor-logout')
def doctor_logout():
    session.pop('doctor', None)
    return redirect('/')

# ═══════════════════════════════════════════════════════════════
# AUTH0 ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback', _external=True))

@app.route('/callback')
def callback():
    try:
        token = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo.get('picture', '')
        }
        session['user'] = {'userinfo': userinfo}
        return redirect('/')
    except Exception:
        # Authorization code expired or was already used (e.g. page refresh)
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True)