from flask import Flask, render_template, request
from diseaseprediction import DiseasePrediction

app = Flask(__name__)
model = DiseasePrediction()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():

    symptoms = [
        request.form.get("symptom1"),
        request.form.get("symptom2"),
        request.form.get("symptom3"),
        request.form.get("symptom4"),
        request.form.get("symptom5")
    ]

    symptoms = [s for s in symptoms if s]

    disease = model.predict(symptoms)

    return render_template("result.html", prediction=disease)

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

if __name__ == "__main__":
    app.run(debug=True)