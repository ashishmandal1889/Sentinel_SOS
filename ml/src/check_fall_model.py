
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "sentinel_fall_detection.pkl"

try:
    model = joblib.load(MODEL_PATH)

    print("Fall-detection model loaded successfully!")
    print("Model type:", type(model).__name__)

    if hasattr(model, "n_features_in_"):
        print("Expected number of features:", model.n_features_in_)

    if hasattr(model, "feature_names_in_"):
        print("Expected feature names:", list(model.feature_names_in_))

except Exception as e:
    print("Could not load the model.")
    print("Error:", e)
