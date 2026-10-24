import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "datasets" / "voice_emotion" / "combined_voice_features.csv"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "evaluation"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)

# Separate features, target, and actor groups
metadata_columns = ["actor_id", "emotion", "file_path"]
X = df.drop(columns=metadata_columns)
y = df["emotion"]
groups = df["actor_id"]

print("Dataset shape:", df.shape)
print("Audio features:", X.shape[1])
print("Number of actors:", groups.nunique())
print("\nEmotion counts:\n", y.value_counts())

# Split by actor so the same actor is not in both sets
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.25,
    random_state=42,
)
train_idx, test_idx = next(splitter.split(X, y, groups=groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

print("\nTraining recordings:", len(X_train))
print("Testing recordings:", len(X_test))
print("Training actors:", groups.iloc[train_idx].nunique())
print("Testing actors:", groups.iloc[test_idx].nunique())

assert set(groups.iloc[train_idx]).isdisjoint(set(groups.iloc[test_idx]))

# Models
models = {
    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=42,
        )),
    ]),
    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ]),
    "SVM": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", SVC(
            kernel="rbf",
            class_weight="balanced",
        )),
    ]),
}

results = []
trained_models = {}

for name, model in models.items():
    print(f"\n{'=' * 50}")
    print("Training:", name)

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    macro_f1 = f1_score(y_test, predictions, average="macro", zero_division=0)

    results.append({
        "model": name,
        "accuracy": accuracy,
        "macro_f1": macro_f1,
    })
    trained_models[name] = model

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions, labels=sorted(y.unique())))
# Plot confusion matrix for the SVM model
svm_model = trained_models["SVM"]
svm_predictions = svm_model.predict(X_test)

labels = sorted(y.unique())

cm = confusion_matrix(
    y_test,
    svm_predictions,
    labels=labels
)

plt.figure(figsize=(10, 7))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    xticklabels=labels,
    yticklabels=labels
)

plt.xlabel("Predicted Emotion")
plt.ylabel("Actual Emotion")
plt.title("SVM Voice Emotion Confusion Matrix")
plt.tight_layout()
plt.savefig("evaluation/svm_confusion_matrix.png", dpi=300, bbox_inches="tight")
plt.show()
# Compare models
results_df = pd.DataFrame(results).sort_values(
    by="macro_f1",
    ascending=False,
)

print("\n===== MODEL COMPARISON =====")
print(results_df.to_string(index=False))

results_df.to_csv(REPORT_DIR / "voice_model_comparison.csv", index=False)

# Save the best model by macro F1
best_name = results_df.iloc[0]["model"]
best_model = trained_models[best_name]

joblib.dump(
    {
        "model": best_model,
        "feature_columns": list(X.columns),
        "classes": list(best_model.classes_),
        "model_name": best_name,
    },
    MODEL_DIR / "voice_emotion_model.pkl",
)

print("\nBest model:", best_name)
print("Saved model:", MODEL_DIR / "voice_emotion_model.pkl")
print("Saved comparison:", REPORT_DIR / "voice_model_comparison.csv")
