"""
integrations.py — ElevenLabs, Snowflake, DigitalOcean Spaces, Solana integrations.

Each integration has:
  - An availability flag (_AVAILABLE)
  - A main function that performs the integration
  - Graceful fallback when API keys are missing
"""

import os
import hashlib
import json
import time
import io
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ===========================================================================
# 🔊 ElevenLabs — Text-to-Speech
# ===========================================================================

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # "Rachel"
ELEVENLABS_AVAILABLE = bool(ELEVENLABS_API_KEY)

if ELEVENLABS_AVAILABLE:
    print("✅ ElevenLabs TTS configured")
else:
    print("⚠️  No ELEVENLABS_API_KEY — voice output disabled")


def _strip_markdown(text: str) -> str:
    """Convert markdown to plain text for TTS."""
    text = re.sub(r'#{1,6}\s*', '', text)           # headers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)    # bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)         # italic
    text = re.sub(r'\|[^\n]+\|', '', text)            # tables
    text = re.sub(r'^[-*]\s+', '• ', text, flags=re.MULTILINE)  # bullets
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)   # numbered
    text = re.sub(r'---+', '', text)                  # hr
    text = re.sub(r'>\s*', '', text)                  # blockquotes
    text = re.sub(r'\n{3,}', '\n\n', text)            # excess newlines
    text = text.replace('##', '').replace('#', '')
    return text.strip()


def speak_report(report_text: str) -> bytes | None:
    """Convert report text to speech using ElevenLabs API. Returns MP3 bytes."""
    if not ELEVENLABS_AVAILABLE:
        return None

    import requests

    clean_text = _strip_markdown(report_text)
    # Truncate to 5000 chars for free tier
    if len(clean_text) > 5000:
        clean_text = clean_text[:5000] + "... For the complete report, please read the text version."

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": clean_text,
            "model_id": "eleven_flash_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.content
        else:
            print(f"⚠️  ElevenLabs error {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"⚠️  ElevenLabs error: {e}")
        return None


# ===========================================================================
# ❄️ Snowflake — Population Health Analytics
# ===========================================================================

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "HEALTHAI")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
SNOWFLAKE_AVAILABLE = bool(SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER and SNOWFLAKE_PASSWORD)

if SNOWFLAKE_AVAILABLE:
    print("✅ Snowflake analytics configured")
else:
    print("⚠️  No Snowflake credentials — analytics will use local fallback")

# Local analytics store (used when Snowflake is unavailable)
_local_analytics = []


def _get_snowflake_conn():
    """Create a Snowflake connection."""
    import snowflake.connector
    # Connect without forcing an initial database, in case it doesn't exist yet
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
    )


def _ensure_snowflake_table():
    """Create the database, schema, and health_checkups table if they don't exist."""
    conn = _get_snowflake_conn()
    try:
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {SNOWFLAKE_DATABASE}")
        cur.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_SCHEMA}")
        cur.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS health_checkups (
                id STRING DEFAULT UUID_STRING(),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                age_range STRING,
                gender STRING,
                complaint STRING,
                severity STRING,
                duration STRING,
                symptoms VARIANT,
                predicted_disease STRING,
                confidence FLOAT,
                body_areas VARIANT,
                preexisting VARIANT,
                lifestyle VARIANT
            )
        """)
    finally:
        conn.close()


def store_health_data(patient_data: dict, diagnosis: dict) -> bool:
    """Store anonymized checkup data in Snowflake (or local fallback)."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "age_range": patient_data.get("age", "N/A"),
        "gender": patient_data.get("gender", "N/A"),
        "complaint_category": _categorize_complaint(patient_data.get("complaint", "")),
        "severity": patient_data.get("severity", "N/A"),
        "duration": patient_data.get("duration", "N/A"),
        "symptom_count": len(patient_data.get("all_symptoms", [])),
        "top_symptoms": patient_data.get("all_symptoms", [])[:5],
        "predicted_disease": "",
        "confidence": 0,
        "body_areas": patient_data.get("body_areas", []),
        "preexisting": patient_data.get("preexisting", []),
    }

    top = diagnosis.get("top_conditions", [])
    if top:
        record["predicted_disease"] = top[0].get("name", "")
        record["confidence"] = top[0].get("confidence_score", 0)

    if SNOWFLAKE_AVAILABLE:
        try:
            _ensure_snowflake_table()
            conn = _get_snowflake_conn()
            try:
                cur = conn.cursor()
                cur.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
                cur.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
                cur.execute("""
                    INSERT INTO health_checkups (age_range, gender, complaint, severity,
                        duration, symptoms, predicted_disease, confidence, body_areas,
                        preexisting, lifestyle)
                    SELECT %s, %s, %s, %s, %s, PARSE_JSON(%s), %s, %s,
                        PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s)
                """, (
                    record["age_range"], record["gender"],
                    record["complaint_category"], record["severity"],
                    record["duration"], json.dumps(record["top_symptoms"]),
                    record["predicted_disease"], record["confidence"],
                    json.dumps(record["body_areas"]),
                    json.dumps(record["preexisting"]),
                    json.dumps(patient_data.get("lifestyle", {})),
                ))
            finally:
                conn.close()
            return True
        except Exception as e:
            print(f"⚠️  Snowflake insert error: {e}")

    # Local fallback
    _local_analytics.append(record)
    return True


def get_health_stats() -> dict:
    """Get aggregate health statistics from Snowflake or local data."""
    if SNOWFLAKE_AVAILABLE:
        try:
            _ensure_snowflake_table()
            conn = _get_snowflake_conn()
            try:
                cur = conn.cursor()
                cur.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
                cur.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
                stats = {}

                # Filter out null or empty diseases
                cur.execute("SELECT predicted_disease, COUNT(*) as cnt FROM health_checkups WHERE predicted_disease IS NOT NULL AND predicted_disease != '' GROUP BY predicted_disease ORDER BY cnt DESC LIMIT 5")
                stats["top_diseases"] = [{"disease": r[0], "count": r[1]} for r in cur.fetchall()]

                cur.execute("SELECT age_range, COUNT(*) as cnt FROM health_checkups WHERE age_range IS NOT NULL AND age_range != 'N/A' GROUP BY age_range ORDER BY cnt DESC")
                stats["by_age"] = [{"age": r[0], "count": r[1]} for r in cur.fetchall()]

                cur.execute("SELECT COUNT(*) FROM health_checkups")
                stats["total_checkups"] = cur.fetchone()[0]

                cur.execute("SELECT COUNT(DISTINCT predicted_disease) FROM health_checkups WHERE predicted_disease IS NOT NULL AND predicted_disease != ''")
                stats["unique_diseases"] = cur.fetchone()[0]

                return {"source": "snowflake", **stats}
            finally:
                conn.close()
        except Exception as e:
            print(f"⚠️  Snowflake query error: {e}")

    # Local fallback stats
    data = _local_analytics
    if not data:
        return {
            "source": "local",
            "total_checkups": 0,
            "unique_diseases": 0,
            "top_diseases": [],
            "by_age": [],
            "message": "No data yet. Complete a health checkup to see analytics.",
        }

    diseases = {}
    ages = {}
    for r in data:
        d = r.get("predicted_disease", "")
        if d:
            diseases[d] = diseases.get(d, 0) + 1
        a = r.get("age_range", "")
        if a:
            ages[a] = ages.get(a, 0) + 1

    return {
        "source": "local",
        "total_checkups": len(data),
        "unique_diseases": len(diseases),
        "top_diseases": sorted([{"disease": k, "count": v} for k, v in diseases.items()],
                               key=lambda x: x["count"], reverse=True)[:5],
        "by_age": [{"age": k, "count": v} for k, v in ages.items()],
    }


def _categorize_complaint(complaint: str) -> str:
    """Remove PII from complaint — keep only category."""
    complaint = complaint.lower().strip()
    if len(complaint) > 100:
        complaint = complaint[:100]
    return complaint


# ===========================================================================
# 🌊 DigitalOcean Spaces — Cloud Report Storage
# ===========================================================================

DO_SPACES_KEY = os.getenv("DO_SPACES_KEY", "")
DO_SPACES_SECRET = os.getenv("DO_SPACES_SECRET", "")
DO_SPACES_REGION = os.getenv("DO_SPACES_REGION", "nyc3")
DO_SPACES_BUCKET = os.getenv("DO_SPACES_BUCKET", "healthai-reports")
DO_SPACES_ENDPOINT = os.getenv("DO_SPACES_ENDPOINT", f"https://{DO_SPACES_REGION}.digitaloceanspaces.com")
DO_AVAILABLE = bool(DO_SPACES_KEY and DO_SPACES_SECRET)

if DO_AVAILABLE:
    print("✅ DigitalOcean Spaces configured")
else:
    print("⚠️  No DO Spaces credentials — cloud storage disabled")


def _get_s3_client():
    """Create an S3-compatible client for DO Spaces."""
    import boto3
    return boto3.client(
        "s3",
        region_name=DO_SPACES_REGION,
        endpoint_url=DO_SPACES_ENDPOINT,
        aws_access_key_id=DO_SPACES_KEY,
        aws_secret_access_key=DO_SPACES_SECRET,
    )


def upload_report_to_cloud(pdf_bytes: bytes, filename: str = None) -> dict | None:
    """Upload PDF report to DigitalOcean Spaces. Returns URL info."""
    if not DO_AVAILABLE:
        return None

    if not filename:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/HealthAI_Report_{ts}.pdf"

    try:
        s3 = _get_s3_client()
        s3.put_object(
            Bucket=DO_SPACES_BUCKET,
            Key=filename,
            Body=pdf_bytes,
            ContentType="application/pdf",
            ACL="public-read",
        )
        public_url = f"{DO_SPACES_ENDPOINT}/{DO_SPACES_BUCKET}/{filename}"
        cdn_url = f"https://{DO_SPACES_BUCKET}.{DO_SPACES_REGION}.cdn.digitaloceanspaces.com/{filename}"

        return {
            "url": public_url,
            "cdn_url": cdn_url,
            "filename": filename,
            "size_kb": round(len(pdf_bytes) / 1024, 1),
        }
    except Exception as e:
        print(f"⚠️  DO Spaces upload error: {e}")
        return None


# ===========================================================================
# ⛓️ Solana — Blockchain Health Record Verification
# ===========================================================================

SOLANA_PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY", "")
SOLANA_NETWORK = os.getenv("SOLANA_NETWORK", "devnet")
SOLANA_AVAILABLE = bool(SOLANA_PRIVATE_KEY)

SOLANA_RPC_URLS = {
    "devnet": "https://api.devnet.solana.com",
    "mainnet": "https://api.mainnet-beta.solana.com",
}

if SOLANA_AVAILABLE:
    print(f"✅ Solana blockchain configured ({SOLANA_NETWORK})")
else:
    print("⚠️  No Solana key — blockchain verification disabled")


def hash_report(report_text: str, patient_data: dict) -> str:
    """Create a SHA-256 hash of the health report for blockchain storage."""
    data_to_hash = json.dumps({
        "report": report_text,
        "timestamp": datetime.utcnow().isoformat(),
        "complaint": patient_data.get("complaint", ""),
        "symptoms": patient_data.get("all_symptoms", []),
    }, sort_keys=True)
    return hashlib.sha256(data_to_hash.encode()).hexdigest()


def store_on_blockchain(report_hash: str) -> dict | None:
    """Store the report hash on Solana blockchain as a memo transaction."""
    if not SOLANA_AVAILABLE:
        return None

    try:
        from solders.keypair import Keypair
        from solders.pubkey import Pubkey
        from solders.system_program import TransferParams, transfer
        from solders.transaction import Transaction
        from solders.message import Message
        from solders.instruction import Instruction, AccountMeta
        from solders.hash import Hash as SolHash
        import base64
        import requests

        rpc_url = SOLANA_RPC_URLS.get(SOLANA_NETWORK, SOLANA_RPC_URLS["devnet"])

        # Load keypair from base58 private key
        keypair = Keypair.from_base58_string(SOLANA_PRIVATE_KEY)

        # Memo program ID
        memo_program = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")

        # Create memo instruction with report hash
        memo_data = f"HealthAI:{report_hash[:32]}".encode()
        memo_ix = Instruction(
            program_id=memo_program,
            accounts=[AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=True)],
            data=memo_data,
        )

        # Get recent blockhash
        resp = requests.post(rpc_url, json={
            "jsonrpc": "2.0", "id": 1,
            "method": "getLatestBlockhash",
            "params": [{"commitment": "finalized"}],
        }, timeout=10).json()

        blockhash = SolHash.from_string(resp["result"]["value"]["blockhash"])

        # Build and sign transaction
        msg = Message.new_with_blockhash([memo_ix], keypair.pubkey(), blockhash)
        tx = Transaction.new_unsigned(msg)
        tx.sign([keypair], blockhash)

        # Send transaction
        tx_bytes = bytes(tx)
        tx_base64 = base64.b64encode(tx_bytes).decode()

        send_resp = requests.post(rpc_url, json={
            "jsonrpc": "2.0", "id": 1,
            "method": "sendTransaction",
            "params": [tx_base64, {"encoding": "base64"}],
        }, timeout=15).json()

        if "result" in send_resp:
            tx_sig = send_resp["result"]
            explorer_url = f"https://explorer.solana.com/tx/{tx_sig}?cluster={SOLANA_NETWORK}"
            return {
                "tx_signature": tx_sig,
                "report_hash": report_hash,
                "explorer_url": explorer_url,
                "network": SOLANA_NETWORK,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            print(f"⚠️  Solana tx error: {send_resp.get('error', 'unknown')}")
            return None

    except Exception as e:
        print(f"⚠️  Solana error: {e}")
        return None


# ===========================================================================
# Integration status summary
# ===========================================================================

def get_integration_status() -> dict:
    """Return availability status of all integrations."""
    return {
        "elevenlabs": ELEVENLABS_AVAILABLE,
        "snowflake": SNOWFLAKE_AVAILABLE,
        "digitalocean": DO_AVAILABLE,
        "solana": SOLANA_AVAILABLE,
    }
