
import pandas as pd
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset paths
features_path = BASE_DIR / "datasets" / "voice_emotion" / "audio_features.csv"
extra_path = BASE_DIR / "datasets" / "voice_emotion" / "audio_extra_features.csv"

# Load datasets
features_df = pd.read_csv(features_path)
extra_df = pd.read_csv(extra_path)

# Inspect the main feature dataset
print("\n===== AUDIO FEATURES =====")
print("Shape:", features_df.shape)
print("\nColumns:")
print(features_df.columns.tolist())
print("\nMissing values:", features_df.isnull().sum().sum())

# Inspect the additional feature dataset
print("\n===== EXTRA AUDIO FEATURES =====")
print("Shape:", extra_df.shape)
print("\nColumns:")
print(extra_df.columns.tolist())
print("\nMissing values:", extra_df.isnull().sum().sum())

# Display emotion distribution
if "emotion" in features_df.columns:
    print("\n===== EMOTION DISTRIBUTION =====")
    print(features_df["emotion"].value_counts())
else:
    print("\nNo column named 'emotion' was found.")
    print("Please check the column names printed above.")
print("\n===== CHECKING DATASET ALIGNMENT =====")

print(
    "Actor IDs match:",
    features_df["actor_id"].equals(extra_df["actor_id"])
)

print(
    "Emotion labels match:",
    features_df["emotion"].equals(extra_df["emotion"])
)

print(
    "File paths match:",
    features_df["file_path"].equals(extra_df["file_path"])
)

print("\nDuplicate file paths in main dataset:",
      features_df["file_path"].duplicated().sum())

print("Duplicate file paths in extra dataset:",
      extra_df["file_path"].duplicated().sum())