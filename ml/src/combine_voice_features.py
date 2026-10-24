
import pandas as pd
from pathlib import Path

# Locate the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset paths
features_path = (
    BASE_DIR / "datasets" / "voice_emotion" / "audio_features.csv"
)
extra_path = (
    BASE_DIR / "datasets" / "voice_emotion" / "audio_extra_features.csv"
)

# Output path
output_path = (
    BASE_DIR / "datasets" / "voice_emotion" / "combined_voice_features.csv"
)

# Load both datasets
features_df = pd.read_csv(features_path)
extra_df = pd.read_csv(extra_path)

# Verify that recordings match
assert features_df["file_path"].equals(extra_df["file_path"]), (
    "File paths do not match. Do not combine the datasets."
)

assert features_df["actor_id"].equals(extra_df["actor_id"]), (
    "Actor IDs do not match."
)

assert features_df["emotion"].equals(extra_df["emotion"]), (
    "Emotion labels do not match."
)

# Select only the additional numerical features
extra_columns = [
    "pitch_mean",
    "pitch_std",
    "energy_mean",
    "energy_std",
]

# Combine the datasets
combined_df = pd.concat(
    [
        features_df,
        extra_df[extra_columns],
    ],
    axis=1,
)

# Save the combined dataset
combined_df.to_csv(output_path, index=False)

# Display the results
print("Combined dataset created successfully!")
print("Shape:", combined_df.shape)
print("Total columns:", len(combined_df.columns))
print("Total audio features:", combined_df.shape[1] - 4)
print("Missing values:", combined_df.isnull().sum().sum())
print("Saved to:", output_path)

print("\nEmotion distribution:")
print(combined_df["emotion"].value_counts())
