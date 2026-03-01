# HealthAI: Human-Health-Disease-Prediction

**HealthAI** is a machine learning–based healthcare system developed by **Team Tech99 (3 members)** for the **Diversion2k26 Hackathon**. The project is designed to enable early detection of potential diseases by analyzing user-provided symptoms, providing data-driven insights to help users make smarter health decisions.

## 🚀 Overview
The system utilizes machine learning algorithms to map a wide array of physical symptoms to potential medical conditions. By offering an accessible way to screen for health issues, it aims to facilitate proactive healthcare management and smarter health analysis.

## ✨ Key Features
*   **Symptom-Based Prediction:** Predicts potential diseases based on a comprehensive list of user-input symptoms.
*   **Machine Learning Engine:** Utilizes specialized scripts (`ml_engine.py` and `model_trainer.py`) to process data and generate accurate predictions.
*   **PDF Report Generation:** Includes functionality to generate reports for users (`pdf_generator.py`).
*   **Health Recommendations:** Provides actionable health insights and recommendations (`recommendations.py`).
*   **Web Interface:** A user-friendly interface built with Python and web technologies.

## 🛠️ Tech Stack
*   **Backend:** Python (98.8%)
*   **Frontend:** HTML, CSS, and JavaScript
*   **Automation/Scripts:** PowerShell and Batchfile
*   **Core Logic:** Machine learning integration for health analysis

## 📂 Project Structure
The repository is organized as follows:
*   `/datasets`: Contains data used for training and testing models.
*   `/models`: Stores trained machine learning models.
*   `/static` & `/templates`: Assets and HTML files for the web interface.
*   `app.py`: The main entry point for the application.
*   `ml_engine.py`: Core machine learning prediction logic.
*   `recommendations.py`: Logic for providing health advice.
*   `pdf_generator.py`: Tool for generating health summary reports.
*   `agents.py` & `integrations.py`: Handles external interactions and specialized tasks.
*   `seed_db.py`: Script for initializing or seeding the project database.

## 📋 Supported Symptoms
The system can analyze a vast range of symptoms, including but not limited to:
*   **General:** Fatigue, high_fever, weight_loss, restlessness, and lethargy.
*   **Skin-related:** Itching, skin_rash, nodal_skin_eruptions, and yellow_crust_ooze.
*   **Digestive:** Stomach_pain, acidity, vomiting, indigestion, and constipation.
*   **Neurological:** Headache, dizziness, altered_sensorium, and slurred_speech.
*   **Respiratory:** Continuous_sneezing, cough, breathlessness, and phlegm.

## 👥 Contributors
Developed with ❤️ by **Team Tech99** (3 members) for the **Diversion2k26 Hackathon**.
