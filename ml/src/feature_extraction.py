import pandas as pd

SENSOR_COLUMNS = [
    "xAcc",
    "yAcc",
    "zAcc",
    "xGyro",
    "yGyro",
    "zGyro"
]

WINDOW_SIZE = 400


def extract_features(sensor_data):
    """
    Extract 24 statistical features from 400 sensor readings.
    """

    if len(sensor_data) != WINDOW_SIZE:
        raise ValueError("Expected exactly 400 sensor readings.")

    if not all(col in sensor_data.columns for col in SENSOR_COLUMNS):
        raise ValueError("Missing one or more required sensor columns.")

    features = {}

    for col in SENSOR_COLUMNS:
        features[f"{col}_mean"] = sensor_data[col].mean()
        features[f"{col}_std"] = sensor_data[col].std()
        features[f"{col}_min"] = sensor_data[col].min()
        features[f"{col}_max"] = sensor_data[col].max()

    return pd.DataFrame([features])