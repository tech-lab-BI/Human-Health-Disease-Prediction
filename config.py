"""
config.py — Application configuration, Auth0 setup, Gemini setup.
"""

import os
import time
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

load_dotenv()

# ---------------------------------------------------------------------------
# Flask Config
# ---------------------------------------------------------------------------
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "health-chatbot-secret-key")

# ---------------------------------------------------------------------------
# Auth0 Config
# ---------------------------------------------------------------------------
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")


def init_oauth(app):
    """Register Auth0 with the Flask app and return the OAuth instance."""
    oauth = OAuth(app)
    oauth.register(
        "auth0",
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        client_kwargs={"scope": "openid profile email"},
        server_metadata_url=f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration",
    )
    return oauth


# ---------------------------------------------------------------------------
# Gemini Config
# ---------------------------------------------------------------------------
GEMINI_AVAILABLE = False
gemini_model = None

try:
    import google.generativeai as genai

    _api_key = os.getenv("GEMINI_API_KEY", "")
    if _api_key:
        genai.configure(api_key=_api_key)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        GEMINI_AVAILABLE = True
        print("✅ Gemini API configured")
    else:
        print("⚠️  No GEMINI_API_KEY — running in offline mode")
except ImportError:
    print("⚠️  google-generativeai not installed — offline mode")


def gemini_call_safe(func, *args, max_retries=2, **kwargs):
    """Call a Gemini function with retry logic. Returns None on failure."""
    global GEMINI_AVAILABLE
    if not GEMINI_AVAILABLE or gemini_model is None:
        return None
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower():
                if attempt < max_retries:
                    time.sleep(2 ** attempt * 2)
                    continue
                else:
                    GEMINI_AVAILABLE = False
                    return None
            else:
                return None
    return None
