
from pathlib import Path

import pandas as pd

from predict_fall import predict_fall


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "datasets" / "fall_detection" / "acc_gyr.csv"

# Load dataset
data = pd.read_csv(DATA_PATH)

print("Dataset loaded:", data.shape)

# Select 400 sensor readings labelled as fall
sample_window = data[data["label"] == "fall"].iloc[:400].copy()

if len(sample_window) != 400:
    raise ValueError("Could not find 400 fall-labelled sensor readings.")

print("Labels in sample window:")
print(sample_window["label"].value_counts())

# Run reusable prediction function
result = predict_fall(sample_window)

print("Prediction:", result["label"])
print("Prediction code:", result["prediction"])

if "fall_probability" in result:
    print("Model-estimated fall probability:", result["fall_probability"])
