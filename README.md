# ⚾ MLB Career Longevity Predictor

**Avery Bishop** · Distributed Systems for Data Science · New College of Florida · Spring 2026

## Live Application
🔗 [MLB Career Longevity Predictor](https://averybishop-mlb-career-predictor-app.streamlit.app/)

## What It Predicts
Given any MLB position player's name, the application retrieves their full career history and predicts how many years they have remaining in their MLB career using a Random Forest regression model trained on 47,991 player-seasons of performance and injury data.

## Pipeline Architecture
Raw Data (GitHub CSV)
↓
S3 (Bronze Layer — raw CSV storage)
↓
Databricks + PySpark (Silver — cleaned, typed, validated)
↓
Databricks + PySpark (Gold — feature table, nulls removed)
↓
MLflow (Model training, experiment tracking, model registry)
↓
S3 (Model artifact + gold CSV storage)
↓
EC2 FastAPI (Live prediction endpoint)
↓
Streamlit Cloud (Public web application)

## Tech Stack
| Layer | Technology |
|---|---|
| Raw Storage | AWS S3 |
| Transformation | Databricks PySpark (silver/gold medallion) |
| ML Training | scikit-learn Random Forest + Databricks MLflow |
| Model Serving | FastAPI on AWS EC2 (t3.micro) |
| Frontend | Streamlit Cloud |

## Model Performance
- **Algorithm:** Random Forest Regressor (100 trees, max depth 10)
- **Target:** Years remaining in MLB career
- **MAE:** 2.53 years
- **R²:** 0.363
- **Training rows:** 47,991 player-seasons (1871–2024)

## Repository Structure
mlb-career-predictor/
├── app.py                        # Streamlit frontend
├── api.py                        # FastAPI backend (EC2)
├── test_project.py               # Instructor test script
├── requirements.txt              # Streamlit dependencies
├── sdm2_cum_inj.csv             # Raw dataset (bronze layer)
├── mlb_career_predictions.ipynb  # Databricks pipeline notebook
└── README.md

## Running the Test Script
```bash
pip install requests
python test_project.py
```

The script verifies three things:
1. The API health check endpoint responds
2. Player lookup returns career history and prediction
3. Direct prediction endpoint returns a valid result

## Notes
- The EC2 prediction API (`http://54.210.153.26:8000`) must be running during grading
- AWS credentials in `api.py` and the Databricks notebook have been replaced with placeholders
- Databricks Community Edition restrictions prevented Delta Lake persistence and direct S3 mounting — the medallion architecture is implemented via in-memory Spark DataFrames with S3 used for bronze storage and model/data artifact export
