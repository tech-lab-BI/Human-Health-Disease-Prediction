from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

# Load trained model (if you have .pkl file)
try:
    model = pickle.load(open("model.pkl", "rb"))
except:
    model = None

# Home Page
@app.route('/')
def home():
    return render_template("index.html")

# Disease Prediction
@app.route('/predict', methods=['POST'])
def predict():
    symptoms = [
        request.form['symptom1'],
        request.form['symptom2'],
        request.form['symptom3'],
        request.form['symptom4'],
        request.form['symptom5']
    ]

    # Dummy Prediction (Replace with real ML prediction)
    if "itching" in symptoms:
        disease = "Fungal Infection"
    elif "nodal_skin_eruptions" in symptoms:
        disease = "Allergy"
    else:
        disease = "Cervical spondylosis"

    return render_template("result.html", disease=disease)

# Doctor Finder
@app.route('/doctor')
def doctor():
    return render_template("doctor.html")

if __name__ == "__main__":
    app.run(debug=True)