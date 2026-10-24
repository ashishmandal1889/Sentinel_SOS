
from pathlib import Path

import joblib
import pandas as pd

from feature_extraction import extract_features


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_DIR / "models" / "sentinel_fall_detection.pkl"

# Required sensor columns
SENSOR_COLUMNS = [
    "xAcc",
    "yAcc",
    "zAcc",
    "xGyro",
    "yGyro",
    "zGyro",
]

WINDOW_SIZE = 400


# Load the trained model once when this module is imported
model = joblib.load(MODEL_PATH)


def predict_fall(sensor_data):
    """
    Predict whether a 400-reading sensor window contains
    fall-related activity.

    Parameters:
        sensor_data (pandas.DataFrame):
            Exactly 400 rows containing the six required sensor columns.

    Returns:
        dict: Prediction result and model confidence, if available.
    """

    if not isinstance(sensor_data, pd.DataFrame):
        raise TypeError("sensor_data must be a pandas DataFrame.")

    if len(sensor_data) != WINDOW_SIZE:
        raise ValueError(
            f"Expected exactly {WINDOW_SIZE} sensor readings; "
            f"received {len(sensor_data)}."
        )

    missing_columns = [
        column for column in SENSOR_COLUMNS
        if column not in sensor_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required sensor columns: {missing_columns}"
        )

    # Keep only the required sensor columns and ensure numeric values
    sensor_data = sensor_data[SENSOR_COLUMNS].copy()

    for column in SENSOR_COLUMNS:
        sensor_data[column] = pd.to_numeric(
            sensor_data[column], errors="raise"
        )

    if sensor_data.isnull().any().any():
        raise ValueError("Sensor data contains missing values.")

    # Extract the same 24 features used during model training
    features = extract_features(sensor_data)

    # Match the exact feature order expected by the trained model
    features = features.reindex(columns=model.feature_names_in_)

    # Predict activity
    prediction = int(model.predict(features)[0])

    result = {
        "prediction": prediction,
        "label": (
            "fall_related"
            if prediction == 1
            else "normal_activity"
        ),
    }

    # Include probability only if the model supports it
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        class_indices = list(model.classes_)
        fall_index = class_indices.index(1)

        result["fall_probability"] = round(
            float(probabilities[fall_index]), 4
        )

    return result
