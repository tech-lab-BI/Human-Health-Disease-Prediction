# HealthAI Setup Guide

## Prerequisites
- **Python 3.10+** (tested with 3.10, 3.11, 3.12)
- Windows, macOS, or Linux
- `pip` and `venv` (comes with Python)

## Installation Steps

### 1. Clone or Extract the Project
```bash
cd HealthAI
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# Required:
#   - FLASK_SECRET_KEY
#   - AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET
#   - GEMINI_API_KEY (for AI features)
# Optional:
#   - ELEVENLABS_API_KEY (for voice output)
#   - SNOWFLAKE_* (for health records storage)
#   - SOLANA_* (for blockchain verification)
```

### 6. Train ML Models (Optional - Models are Pre-trained)
If you want to retrain the ML models:
```bash
python model_trainer.py
```

This will:
- Load Training.csv and Testing.csv from the `datasets/` folder
- Train Random Forest and SVM classifiers
- Save models to `models/` directory
- Generate metadata.json with accuracy statistics

### 7. Run the Application
```bash
# Linux/macOS
python app.py

# Windows
python app.py
```

The app will start at: `http://localhost:5000`

## Project Structure

```
HealthAI/
├── app.py                    # Flask main application
├── config.py                 # Auth0, Gemini, Flask config
├── constants.py              # Symptom categories, body areas
├── ml_engine.py              # ML prediction & symptom extraction
├── agents.py                 # Gemini AI agents (diagnosis, recommendations)
├── integrations.py           # ElevenLabs, Snowflake, Solana integrations
├── pdf_generator.py          # PDF report generation
├── recommendations.py        # Local recommendation fallback data
├── model_trainer.py          # Train/retrain ML models
├── seed_db.py                # Bulk load data to Snowflake
│
├── datasets/
│   ├── Training.csv          # Historical patient data
│   └── Testing.csv           # Test data for validation
│
├── models/
│   ├── rf_disease_model.pkl  # Random Forest classifier
│   ├── svm_disease_model.pkl # SVM classifier
│   ├── label_encoder.pkl     # Disease label encoder
│   └── metadata.json         # Model metadata & accuracy
│
├── templates/
│   └── index.html            # Main UI (login, wizard, results)
│
├── static/
│   ├── app.js                # Frontend logic & wizard
│   └── style.css             # Modern UI styling
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # Project documentation
```

## API Endpoints

### Authentication
- `GET /login` - Login via Auth0
- `GET /callback` - Auth0 callback
- `GET /logout` - Logout

### Health Assessment
- `GET /api/status` - Check API status (Gemini, Models, Integrations)
- `GET /api/symptoms` - Get all available symptoms
- `POST /api/generate-steps` - Generate dynamic wizard steps
- `POST /api/analyze` - Run diagnosis (ML + AI)

### Reports & Integration
- `GET /api/download-report` - Download PDF report
- `POST /api/speak-report` - Text-to-speech output (ElevenLabs)
- `POST /api/cloud-save` - Save report to cloud (DigitalOcean Spaces)
- `POST /api/blockchain-verify` - Store hash on Solana blockchain
- `GET /api/health-stats` - Get personal health statistics (Snowflake)
- `GET /api/my-records` - Retrieve past health records

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_SECRET_KEY` | ✅ | Secret for session encryption |
| `AUTH0_DOMAIN` | ✅ | Auth0 domain (e.g., `dev-xxx.auth0.com`) |
| `AUTH0_CLIENT_ID` | ✅ | Auth0 app client ID |
| `AUTH0_CLIENT_SECRET` | ✅ | Auth0 app client secret |
| `GEMINI_API_KEY` | ✅ | Google Gemini API key |
| `ELEVENLABS_API_KEY` | ❌ | ElevenLabs API key (voice output) |
| `SNOWFLAKE_ACCOUNT` | ❌ | Snowflake account ID |
| `SNOWFLAKE_USER` | ❌ | Snowflake user |
| `SNOWFLAKE_PASSWORD` | ❌ | Snowflake password |
| `SOLANA_PRIVATE_KEY` | ❌ | Solana keypair (base58) |
| `SOLANA_NETWORK` | ❌ | Solana network: `devnet` or `mainnet` |

## Quick Start (Development)

```bash
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
cp .env.example .env

# 2. Edit .env with your API keys (at minimum: GEMINI_API_KEY, AUTH0_*)

# 3. Install & Run
pip install -r requirements.txt
python app.py

# 4. Visit http://localhost:5000
```

## Features

✅ **Multi-Agent AI Diagnosis** - Gemini AI with Rule-Based ML  
✅ **ML Models** - Random Forest + SVM for 130+ diseases  
✅ **132 Symptoms** - Comprehensive symptom database  
✅ **PDF Reports** - Downloadable health assessments  
✅ **Text-to-Speech** - ElevenLabs audio narration  
✅ **Cloud Storage** - DigitalOcean Spaces integration  
✅ **Blockchain Verification** - Solana report hashing  
✅ **Auth0 Login** - Secure OpenID Connect authentication  
✅ **Snowflake DB** - Long-term health records  

## Troubleshooting

### Models not loading
```
❌ Could not load ML models
```
**Solution:** Run `python model_trainer.py` to train models first

### Gemini API errors
```
⚠️  No GEMINI_API_KEY — running in offline mode
```
**Solution:** Add `GEMINI_API_KEY` to your `.env` file

### Auth0 configuration errors
**Solution:** Verify `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, and `AUTH0_CLIENT_SECRET` in `.env`

### Port 5000 already in use
```bash
# Change Flask port
set FLASK_ENV=development
set FLASK_DEBUG=1
python app.py  # Will use port 5000, or configure in code
```

## License

MIT License - Use for educational and research purposes.

## Support

For issues or questions, please refer to documentation in `README.md` and code comments.
