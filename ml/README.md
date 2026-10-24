# SentinelSOS — Machine Learning Module

## Overview
SentinelSOS is an emergency-response project designed to help identify potential emergencies using signals such as sensor readings and voice-related features.

This folder contains the machine-learning code, trained models, evaluation reports, and testing scripts developed for the SentinelSOS project.

## Machine Learning Components

### 1. Fall Detection
The fall-detection model uses accelerometer and gyroscope readings to classify a sensor window as either a normal activity or a potential fall-related event.

**Input:**
- 400 consecutive sensor readings
- Six sensor columns: `xAcc`, `yAcc`, `zAcc`, `xGyro`, `yGyro`, `zGyro`

**Features:**
- Mean
- Standard deviation
- Minimum
- Maximum

These four statistics are calculated for each of the six sensor columns, producing 24 features per window.

**Model:** Random Forest Classifier

**Files:**
- `src/feature_extraction.py`
- `src/predict_fall.py`
- `src/train_fall_detection.py`
- `src/test_fall_prediction.py`
- `models/sentinel_fall_detection.pkl`
- `reports/fall_detection_report.txt`

### 2. Voice Emotion Classification
The voice-emotion model classifies extracted audio features into emotion categories. It was trained using the RAVDESS acted-speech dataset.

**Features include:**
- Mel-frequency cepstral coefficients (MFCCs)
- Pitch statistics
- Energy statistics

**Model:** Support Vector Machine (SVM)

**Files:**
- `src/inspect_voice_data.py`
- `src/combine_voice_features.py`
- `src/train_voice_emotion.py`
- `src/test_voice_emotion.py`
- `models/voice_emotion_model.pkl`
- `evaluation/voice_model_comparison.csv`
- `evaluation/svm_confusion_matrix.png`
- `reports/voice_emotion_baseline_report.txt`

The voice-emotion model is an experimental baseline. Emotion classification alone does not establish that a person is experiencing an emergency.

## Project Structure

```text
SentinelSOS_ML/
├── datasets/
├── models/
├── src/
├── evaluation/
├── reports/
├── requirements.txt
└── README.md
```

## Setup

1. Install Python 3.
2. Open a terminal in this folder.
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Testing

Run the fall-detection test:

```bash
python src/test_fall_prediction.py
```

Run the voice-emotion test:

```bash
python src/test_voice_emotion.py
```

These scripts perform basic checks that the trained models can load and produce predictions.

## Limitations

- The models are prototypes and have not been validated for real-world emergency detection.
- The fall-detection model needs evaluation on independent recordings and real-world scenarios.
- The voice-emotion model uses acted speech and has limited classification performance.
- A model prediction must not be treated as confirmation of an emergency.
- Integration with the SentinelSOS backend requires compatible preprocessing, input validation, and error handling.

## Integration Notes

The fall-detection prediction function expects a window containing exactly 400 rows of numeric sensor readings with the six required sensor columns.

The voice-emotion model expects the same feature columns and preprocessing used during training. Raw audio cannot be passed directly to the saved classifier without the appropriate feature-extraction pipeline.

The ML module is kept separate from the backend so that the team can integrate it without unintentionally modifying backend files.