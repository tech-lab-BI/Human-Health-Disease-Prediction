"""
model_trainer.py — Train Random Forest and SVM classifiers on the disease-symptom dataset.

Saves:
  models/rf_disease_model.pkl   — trained Random Forest model
  models/svm_disease_model.pkl  — trained SVM model
  models/label_encoder.pkl      — label encoder for disease labels
  models/metadata.json          — symptom list, disease list, accuracy stats
"""

import os
import json
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_CSV = os.path.join(BASE_DIR, "datasets", "Training.csv")
TEST_CSV = os.path.join(BASE_DIR, "datasets", "Testing.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("📂 Loading training data...")
train_df = pd.read_csv(TRAIN_CSV)
test_df = pd.read_csv(TEST_CSV)

# Clean column names
train_df.columns = [c.strip() for c in train_df.columns]
test_df.columns = [c.strip() for c in test_df.columns]

# Separate features and target
X_train = train_df.drop("prognosis", axis=1)
y_train = train_df["prognosis"].str.strip()

X_test = test_df.drop("prognosis", axis=1)
y_test = test_df["prognosis"].str.strip()

# Get symptom and disease lists
symptoms = [col.strip().replace("_", " ") for col in X_train.columns]
symptom_columns = list(X_train.columns)  # raw column names for model input
diseases = sorted(y_train.unique().tolist())

print(f"   ✅ {len(train_df)} training samples, {len(test_df)} test samples")
print(f"   ✅ {len(symptoms)} symptoms, {len(diseases)} diseases")

# ---------------------------------------------------------------------------
# Encode labels
# ---------------------------------------------------------------------------
le = LabelEncoder()
le.fit(y_train.tolist() + y_test.tolist())
y_train_enc = le.transform(y_train)
y_test_enc = le.transform(y_test)

# ---------------------------------------------------------------------------
# Train Random Forest
# ---------------------------------------------------------------------------
print("\n🧠 Training Random Forest classifier...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1,
)
rf_model.fit(X_train.values, y_train_enc)
print("   ✅ Random Forest training complete")

# ---------------------------------------------------------------------------
# Train SVM
# ---------------------------------------------------------------------------
print("\n🧠 Training SVM classifier...")
svm_model = SVC(
    kernel="rbf",
    probability=True,
    random_state=42
)
svm_model.fit(X_train.values, y_train_enc)
print("   ✅ SVM training complete")

# ---------------------------------------------------------------------------
# Evaluate both models
# ---------------------------------------------------------------------------
print("\n📊 Evaluating Random Forest on test set...")
rf_pred = rf_model.predict(X_test.values)
rf_accuracy = accuracy_score(y_test_enc, rf_pred)
print(f"   🎯 RF Accuracy: {rf_accuracy * 100:.2f}%")
print("\n" + classification_report(y_test, le.inverse_transform(rf_pred)))

print("\n📊 Evaluating SVM on test set...")
svm_pred = svm_model.predict(X_test.values)
svm_accuracy = accuracy_score(y_test_enc, svm_pred)
print(f"   🎯 SVM Accuracy: {svm_accuracy * 100:.2f}%")
print("\n" + classification_report(y_test, le.inverse_transform(svm_pred)))

# ---------------------------------------------------------------------------
# Save models + metadata
# ---------------------------------------------------------------------------
rf_path = os.path.join(MODEL_DIR, "rf_disease_model.pkl")
svm_path = os.path.join(MODEL_DIR, "svm_disease_model.pkl")
encoder_path = os.path.join(MODEL_DIR, "label_encoder.pkl")
metadata_path = os.path.join(MODEL_DIR, "metadata.json")

with open(rf_path, "wb") as f:
    pickle.dump(rf_model, f)
print(f"\n💾 Random Forest model saved to {rf_path}")

with open(svm_path, "wb") as f:
    pickle.dump(svm_model, f)
print(f"💾 SVM model saved to {svm_path}")

with open(encoder_path, "wb") as f:
    pickle.dump(le, f)
print(f"💾 Label encoder saved to {encoder_path}")

metadata = {
    "symptoms": symptoms,
    "symptom_columns": symptom_columns,
    "diseases": diseases,
    "rf_accuracy": round(rf_accuracy * 100, 2),
    "svm_accuracy": round(svm_accuracy * 100, 2),
    "n_training_samples": len(train_df),
    "n_test_samples": len(test_df),
    "n_symptoms": len(symptoms),
    "n_diseases": len(diseases),
    "models": {
        "RandomForestClassifier": {"n_estimators": 200},
        "SVC": {"kernel": "rbf"}
    }
}

with open(metadata_path, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)
print(f"💾 Metadata saved to {metadata_path}")

print(f"\n✅ Done! RF Accuracy: {rf_accuracy * 100:.2f}%, SVM Accuracy: {svm_accuracy * 100:.2f}%")
