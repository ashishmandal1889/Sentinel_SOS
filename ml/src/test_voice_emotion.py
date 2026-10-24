from pathlib import Path
import joblib
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_DIR / "models" / "voice_emotion_model.pkl"
DATA_PATH = PROJECT_DIR / "datasets" / "voice_emotion" / "combined_voice_features.csv"

# Load the saved model
saved_model = joblib.load(MODEL_PATH)

print("Voice-emotion model loaded successfully!")

# Load the dataset
data = pd.read_csv(DATA_PATH)

# Select one sample
sample = data.iloc[[0]]

# Get the expected feature columns
feature_columns = saved_model["feature_columns"]
model = saved_model["model"]

# Prepare the sample
X_sample = sample[feature_columns]

# Predict the emotion
prediction = model.predict(X_sample)

print("Actual emotion:", sample["emotion"].iloc[0])
print("Predicted emotion:", prediction[0])