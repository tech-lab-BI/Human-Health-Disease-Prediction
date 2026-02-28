import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

MODEL_FILE = "disease_model.pkl"

class DiseasePrediction:

    def __init__(self):
        if os.path.exists(MODEL_FILE):
            self.load_model()
        else:
            self.train_model()

    def train_model(self):
        # Load datasets
        train_df = pd.read_csv("training.csv")
        test_df = pd.read_csv("Testing.csv")

        X_train = train_df.drop("prognosis", axis=1)
        y_train = train_df["prognosis"]

        X_test = test_df.drop("prognosis", axis=1)
        y_test = test_df["prognosis"]

        self.symptom_columns = X_train.columns.tolist()

        # Encode diseases
        self.encoder = LabelEncoder()
        y_train_encoded = self.encoder.fit_transform(y_train)
        y_test_encoded = self.encoder.transform(y_test)

        # Train model
        self.model = RandomForestClassifier(n_estimators=200, random_state=42)
        self.model.fit(X_train, y_train_encoded)

        # Check accuracy
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test_encoded, predictions)
        print("Model Accuracy:", round(accuracy * 100, 2), "%")

        # Save model
        joblib.dump({
            "model": self.model,
            "encoder": self.encoder,
            "symptoms": self.symptom_columns
        }, MODEL_FILE)

        print("Model trained and saved.")

    def load_model(self):
        data = joblib.load(MODEL_FILE)
        self.model = data["model"]
        self.encoder = data["encoder"]
        self.symptom_columns = data["symptoms"]

    def predict(self, symptom_list):
        input_data = np.zeros(len(self.symptom_columns))

        for symptom in symptom_list:
            symptom = symptom.strip().lower()

            if symptom in self.symptom_columns:
                index = self.symptom_columns.index(symptom)
                input_data[index] = 1

        input_df = pd.DataFrame([input_data], columns=self.symptom_columns)

        prediction = self.model.predict(input_df)
        disease = self.encoder.inverse_transform(prediction)

        return disease[0]