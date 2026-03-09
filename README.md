# HealthAI: Advanced Disease Prediction & Health Assistant

**HealthAI** is a comprehensive, multi-agent healthcare application developed by **Team Tech99** for the **Diversion2k26 Hackathon**. It combines traditional Machine Learning with Generative AI (Google Gemini) to provide users with accurate disease predictions, personalized health recommendations, and beautifully formatted medical reports based on their symptoms.

---

## ✨ Key Features

- **🗣️ Natural Language & Voice Input:** Users can describe their symptoms naturally by typing or speaking (using the Web Speech API).
- **🤖 Multi-Agent AI System:**
  - **Symptom Extraction:** Gemini AI extracts precise medical symptoms from the user's natural language complaint.
  - **ML Prediction Engine:** An ensemble of Random Forest and Support Vector Machine (SVM) models predicts across 41 possible diseases using a 132-symptom matrix.
  - **AI Physician:** Refines the ML diagnosis and provides personalized, actionable health and lifestyle recommendations.
- **📄 Comprehensive PDF Reports:** Automatically generates detailed, downloadable medical reports summarizing the checkup.
- **🔊 Voice Synthesis (TTS):** Integrates with ElevenLabs to read the diagnosis and recommendations aloud to the user.
- **🔐 Secure Authentication:** User accounts and login flows powered by Auth0.
- **☁️ Cloud Database & Analytics:** Integrates with Snowflake to securely store anonymized health data, retrieve past user prescriptions, and generate population health trends.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Generative AI:** Google Gemini API (`google-generativeai`)
- **Voice:** ElevenLabs API, Web Speech API
- **Database:** Snowflake
- **Authentication:** Auth0
- **Frontend:** HTML5, CSS3, Vanilla JavaScript

---

## 📂 Project Structure

```text
├── app.py                 # Main Flask application and API routing
├── config.py              # Environment variable and configuration loading
├── integrations.py        # Snowflake database connections & Auth0 integration
├── agents.py              # Gemini AI agent prompts and logic
├── ml_engine.py           # Machine learning model loading and prediction logic
├── recommendations.py     # Local fallback logic for treatments if AI is offline
├── pdf_generator.py       # PDF creation logic for downloadable reports
├── requirements.txt       # Python package dependencies
├── datasets/              # Original training datasets and symptom mappings
├── models/                # Pre-trained ML models (.pkl files)
├── static/                # CSS stylesheet (style.css) and JavaScript (app.js)
└── templates/             # HTML files (index.html)
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.9+** installed.

### 2. Clone the Repository
```bash
git clone https://github.com/tech-lab-BI/Human-Health-Disease-Prediction.git
cd Human-Health-Disease-Prediction
```

### 3. Install Dependencies
Create a virtual environment and install the required Python packages:
```bash
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory. You must configure the following key variables for the application to function fully. (See `.env.example` if available).

```ini
# Flask Setup
FLASK_SECRET_KEY=your_secure_random_string
FLASK_DEBUG=True
PORT=5000

# Auth0 (For User Login)
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret

# AI & Voice 
GEMINI_API_KEY=your_google_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_preferred_voice_id

# Snowflake Database (My Past Prescriptions & Analytics)
SNOWFLAKE_ACCOUNT=your_snowflake_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=your_schema
```

*Note: The application is designed to degrade gracefully. If Snowflake or ElevenLabs credentials are not provided, those specific features will disable themselves without crashing the application.*

### 5. Run the Application
Start the Flask server:
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

---

## 📋 Supported Diseases
The underlying Machine Learning model is trained on a dataset covering **41 distinct conditions**, ranging from common ailments (Common Cold, Fungal Infections, Allergies) to more severe conditions (Malaria, Dengue, Pneumonia, Heart Disease).

---

## 👥 Contributors
Developed with ❤️ by **Team Tech99** for the **Diversion2k26 Hackathon**.

Hi happy ending
