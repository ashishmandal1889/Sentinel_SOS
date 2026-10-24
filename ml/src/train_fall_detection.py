from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from feature_extraction import extract_features


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_DIR / "datasets" / "fall_detection" / "acc_gyr.csv"
MODEL_PATH = PROJECT_DIR / "models" / "sentinel_fall_detection.pkl"
REPORT_PATH = PROJECT_DIR / "reports" / "fall_detection_report.txt"

SENSOR_COLUMNS = [
    "xAcc", "yAcc", "zAcc",
    "xGyro", "yGyro", "zGyro"
]

WINDOW_SIZE = 400
FALL_LABELS = {"fall", "rfall", "lfall"}


def build_window_dataset(data):
    """Extract features from valid windows of sensor readings."""

    required_columns = SENSOR_COLUMNS + ["label"]

    missing = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    data = data[required_columns].copy()

    for column in SENSOR_COLUMNS:
        data[column] = pd.to_numeric(
            data[column], errors="raise"
        )

    feature_rows = []
    targets = []

    for start in range(
        0, len(data) - WINDOW_SIZE + 1, WINDOW_SIZE
    ):
        window = data.iloc[start:start + WINDOW_SIZE]

        labels = (
            window["label"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # Skip windows containing mixed activity labels.
        if labels.nunique() != 1:
            continue

        activity = labels.iloc[0]

        features = extract_features(
            window[SENSOR_COLUMNS]
        )

        feature_rows.append(features.iloc[0].to_dict())

        target = 1 if activity in FALL_LABELS else 0
        targets.append(target)

    if not feature_rows:
        raise ValueError("No valid sensor windows were created.")

    X = pd.DataFrame(feature_rows)
    y = pd.Series(targets, name="target", dtype="int64")

    return X, y


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)

    print("Dataset loaded:", data.shape)

    X, y = build_window_dataset(data)

    print("Window dataset:", X.shape)
    print("\nTarget counts (0=normal, 1=fall-related):")
    print(y.value_counts().sort_index())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    print("\nTraining windows:", len(X_train))
    print("Testing windows:", len(X_test))

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    print("\nTraining model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    matrix = confusion_matrix(
        y_test, predictions, labels=[0, 1]
    )

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["normal_activity", "fall_related"],
        zero_division=0,
    )

    # Save the trained model.
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # Save the evaluation report.
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    report_text = (
        "SentinelSOS Fall-Detection Evaluation\n"
        "=====================================\n"
        f"Dataset rows: {len(data)}\n"
        f"Valid windows: {len(X)}\n"
        f"Window size: {WINDOW_SIZE}\n"
        f"Training windows: {len(X_train)}\n"
        f"Testing windows: {len(X_test)}\n"
        f"Accuracy: {accuracy:.4f}\n\n"
        "Confusion matrix (labels 0, 1):\n"
        f"{matrix}\n\n"
        "Classification report:\n"
        f"{report}\n"
        "Limitation: Random window splitting may place related "
        "activity windows in both sets. Grouped validation and "
        "real-world testing are still needed.\n"
    )

    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print("\nAccuracy:", round(accuracy, 4))
    print("\nConfusion matrix:")
    print(matrix)
    print("\nClassification report:")
    print(report)
    print("\nSaved model:", MODEL_PATH)
    print("Saved report:", REPORT_PATH)

    print(
        "\nNote: These results do not establish "
        "real-world emergency-detection reliability."
    )


if __name__ == "__main__":
    main()