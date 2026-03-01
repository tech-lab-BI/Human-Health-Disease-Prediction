# 🚀 HealthAI Deployment Guide

**Complete guide for deploying HealthAI to production**

---

## 📋 Table of Contents
1. [Pre-Deployment Setup](#pre-deployment-setup)
2. [Heroku (Recommended)](#heroku-easiest)
3. [Docker (Portable)](#docker-portable)
4. [Google Cloud Run](#google-cloud-run)
5. [Traditional VPS](#traditional-vps)
6. [Verification & Troubleshooting](#verification--troubleshooting)
7. [Reference Commands](#reference-commands)

---

## Pre-Deployment Setup

### Step 1A: Get API Keys (15 minutes)

**1. Auth0 (Free)**
- Go to https://auth0.com/signup
- Create account → Applications → Create "Regular Web Apps"
- In Settings tab, copy:
  - `AUTH0_DOMAIN` (e.g., dev-abc123.auth0.com)
  - `AUTH0_CLIENT_ID` (e.g., abc123xyz456)
  - `AUTH0_CLIENT_SECRET` (e.g., secret_key_here)

**2. Google Gemini API (Free)**
- Go to https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Copy → `GEMINI_API_KEY`

**3. Flask Secret Key (Free)**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the 64-char output → `FLASK_SECRET_KEY`

**4. Optional Keys**
- ElevenLabs (text-to-speech) — https://elevenlabs.io
- Snowflake (health records) — https://signup.snowflake.com
- DigitalOcean Spaces (cloud) — $5/month
- Solana (blockchain) — devnet (free)

### Step 1B: Create .env File
```powershell
cd d:\check\HealthAI
Copy-Item .env.example .env
notepad .env
```

**Fill in 4 required keys:**
```env
FLASK_SECRET_KEY=<your-64-char-key>
AUTH0_DOMAIN=<your-domain>
AUTH0_CLIENT_ID=<your-id>
AUTH0_CLIENT_SECRET=<your-secret>
GEMINI_API_KEY=<your-key>
```

### Step 1C: Test Locally
```powershell
# Install dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run app
python app.py

# Visit: http://localhost:5000
# Test login: Click "Sign In" → Should go to Auth0
# Stop: Ctrl+C
```

---

# Heroku (Easiest)

## Quick Deploy (10 minutes)

### 1. Install Heroku CLI
- Download: https://devcenter.heroku.com/articles/heroku-cli
- Restart PowerShell after install
```powershell
heroku --version   # Verify installation
heroku login        # Opens browser to login
```

### 2. Prepare Files
```powershell
# Create Procfile
"web: gunicorn app:app" | Out-File Procfile -Encoding utf8

# Create runtime.txt
"python-3.11.5" | Out-File runtime.txt -Encoding utf8

# Verify
ls Procfile, runtime.txt
```

### 3. Create Heroku App
```powershell
heroku apps:create healthai-yourname
# Output: https://healthai-yourname.herokuapp.com
```

### 4. Set Environment Variables
```powershell
heroku config:set FLASK_SECRET_KEY="<your-64-char-key>"
heroku config:set AUTH0_DOMAIN="dev-abc123.auth0.com"
heroku config:set AUTH0_CLIENT_ID="abc123xyz"
heroku config:set AUTH0_CLIENT_SECRET="secret_here"
heroku config:set GEMINI_API_KEY="AIzaSyC..."

# Verify
heroku config
```

### 5. Update Auth0
1. Go to https://manage.auth0.com/dashboard
2. Applications → Your app → Settings
3. Update **Allowed Callback URLs:**
   ```
   https://healthai-yourname.herokuapp.com/callback
   ```
4. Update **Allowed Logout URLs:**
   ```
   https://healthai-yourname.herokuapp.com/
   ```
5. Save Changes

### 6. Deploy
```powershell
git add Procfile runtime.txt .env.example
git commit -m "Add Heroku deployment files"
git push heroku main

# Wait 2-3 minutes...
# heroku open with open your live app
```

### 7. Verify
```powershell
heroku logs --tail          # Check logs
curl https://healthai-yourname.herokuapp.com/api/status
```

---

# Docker (Portable)

## Setup & Deploy

### 1. Install Docker
- Download: https://www.docker.com/products/docker-desktop
- Install and restart computer
```powershell
docker --version
docker run hello-world
```

### 2. Create Dockerfile
```powershell
"FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c ""import requests; requests.get('http://localhost:5000/api/status', timeout=2)""

CMD [""gunicorn"", ""--bind"", ""0.0.0.0:5000"", ""--workers"", ""4"", ""--timeout"", ""60"", ""app:app""]" | Out-File Dockerfile -Encoding utf8
```

### 3. Test Locally
```powershell
# Build image
docker build -t healthai:latest .

# Run
docker run -p 5000:5000 `
  -e FLASK_SECRET_KEY="your-key" `
  -e AUTH0_DOMAIN="your-domain" `
  -e AUTH0_CLIENT_ID="your-id" `
  -e AUTH0_CLIENT_SECRET="your-secret" `
  -e GEMINI_API_KEY="your-key" `
  healthai:latest

# Visit: http://localhost:5000
# Stop: Ctrl+C
```

### 4. Deploy to Docker Hub (Optional)
```powershell
docker login
docker tag healthai:latest yourusername/healthai:latest
docker push yourusername/healthai:latest
```

### 5. Deploy to Cloud
**Option A: DigitalOcean**
1. Create Ubuntu 22.04 droplet ($5/month)
2. SSH into droplet
3. Install Docker
4. Pull and run:
```bash
docker run -d -p 80:5000 \
  -e FLASK_SECRET_KEY="..." \
  -e AUTH0_DOMAIN="..." \
  yourusername/healthai:latest
```

**Option B: AWS EC2** — Same as DigitalOcean

---

# Google Cloud Run

## One-Command Deploy

### 1. Setup
```powershell
# Create account: https://cloud.google.com/run
# Install CLI: https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project healthai-yourproject
```

### 2. Create .gcloudignore
```powershell
@"
venv/
__pycache__/
.env
.git
*.pyc
"@ | Out-File .gcloudignore -Encoding utf8
```

### 3. Deploy
```powershell
gcloud run deploy healthai `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --set-env-vars FLASK_SECRET_KEY="key",AUTH0_DOMAIN="domain",AUTH0_CLIENT_ID="id",AUTH0_CLIENT_SECRET="secret",GEMINI_API_KEY="key"
```

### 4. Update Auth0
Add callback URL in Auth0 dashboard:
```
https://healthai-abc123.run.app/callback
```

---

# Traditional VPS

## Ubuntu/Linux Server Setup

### 1. Create Server
- Provider: DigitalOcean, Linode, AWS EC2, Azure
- Choose: Ubuntu 22.04, $5-10/month
- SSH into server

### 2. Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx -y

git clone https://github.com/yourname/healthai.git
cd healthai
```

### 3. Virtual Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

### 4. Create .env
```bash
nano .env
# Paste your 4 keys
# Save: Ctrl+X, Y, Enter
```

### 5. Create Systemd Service
```bash
sudo nano /etc/systemd/system/healthai.service
```

Paste:
```ini
[Unit]
Description=HealthAI Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/root/healthai
Environment="PATH=/root/healthai/venv/bin"
EnvironmentFile=/root/healthai/.env
ExecStart=/root/healthai/venv/bin/gunicorn --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable healthai
sudo systemctl start healthai
```

### 6. Setup Nginx
```bash
sudo nano /etc/nginx/sites-available/healthai
```

Paste:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/healthai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Enable HTTPS
```bash
sudo certbot --nginx -d yourdomain.com
```

### 8. Update Auth0
Add to Auth0 dashboard:
```
https://yourdomain.com/callback
```

---

## Verification & Troubleshooting

### Test Health Check
```powershell
curl https://healthai-yourname.herokuapp.com/api/status

# Expected:
{
  "gemini_available": true,
  "ml_model_loaded": true,
  "n_diseases": 41,
  "n_symptoms": 132
}
```

### Test Full Flow
1. Visit your URL in browser
2. Click "Sign In to Start Checkup"
3. Type: "I have a persistent cough and fever"
4. Click "Next" through steps
5. Click "Analyze" → Wait for diagnosis
6. Click "Download Report" → PDF downloads

### Common Issues

| Error | Solution |
|-------|----------|
| FLASK_SECRET_KEY not set | `heroku config:set FLASK_SECRET_KEY="..."` |
| Auth0 login fails | Check callback URL matches exactly |
| Models not loading | Ensure `models/` folder is deployed |
| 502 Bad Gateway | Check logs: `heroku logs --tail` |
| Port already in use | Use different port: `set PORT=8000` |

### View Logs
```powershell
# Heroku
heroku logs --tail

# Docker
docker logs <container-id>

# Linux VPS
sudo journalctl -u healthai -f
```

---

## Reference Commands

### Heroku
```powershell
heroku config                    # View env variables
heroku config:set KEY=VALUE      # Set variable
heroku logs --tail              # View logs
heroku restart                  # Restart app
heroku open                     # Open in browser
heroku ps                       # Show running processes
heroku destroy                  # Delete app
```

### Docker
```powershell
docker build -t healthai .      # Build image
docker run -p 5000:5000 healthai  # Run container
docker ps                       # List running containers
docker logs <id>                # View logs
docker stop <id>                # Stop container
docker push user/healthai       # Push to Docker Hub
```

### Google Cloud
```powershell
gcloud run deploy healthai --source .
gcloud run services list
gcloud run services delete healthai
```

### Linux VPS
```bash
systemctl status healthai       # Check status
systemctl restart healthai      # Restart
systemctl logs -f               # View logs
tail -f /var/log/healthai.log   # App logs
```

---

## Success Checklist

- [ ] All 4 API keys obtained
- [ ] .env file created with credentials
- [ ] Local test successful (`python app.py` works)
- [ ] Heroku/Docker/Cloud account created
- [ ] Deployment completed without errors
- [ ] Auth0 callback URLs configured
- [ ] App loads in browser ✅
- [ ] Login works ✅
- [ ] Analysis completes ✅
- [ ] PDF downloads ✅
- [ ] No errors in logs ✅

---

**Your HealthAI is live! 🎉**

Share your URL and enjoy your AI health assistant!
