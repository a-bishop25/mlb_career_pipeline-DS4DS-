from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import pickle
import numpy as np
import pandas as pd
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS credentials (input own before running)
AWS_ACCESS_KEY = "XXXXXXXXXXXXXXXXXXXX"
AWS_SECRET_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
BUCKET = "mlb-career-pipeline-ds-997099833889-us-east-1-an"

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name="us-east-1"
)

# Load model from S3
s3.download_file(BUCKET, "model/mlb_model.pkl", "/tmp/mlb_model.pkl")
with open("/tmp/mlb_model.pkl", "rb") as f:
    model = pickle.load(f)
print("Model loaded successfully!")

# Load player data from S3
csv_obj = s3.get_object(Bucket=BUCKET, Key="data/mlb_gold_named.csv")
df = pd.read_csv(io.BytesIO(csv_obj["Body"].read()))
df["nameFirst"] = df["nameFirst"].str.lower().str.strip()
df["nameLast"] = df["nameLast"].str.lower().str.strip()
print(f"Player data loaded: {len(df)} rows")

FEATURES = [
    "age", "wOBA", "lag_wOBA", "lag_PA", "career_PA",
    "career_G", "years_in_league", "total_injuries",
    "avg_severity", "career_injuries", "career_severity",
    "missed_prev_year"
]

class PlayerInput(BaseModel):
    age: float
    wOBA: float
    lag_wOBA: float
    lag_PA: float
    career_PA: float
    career_G: float
    years_in_league: float
    total_injuries: float
    avg_severity: float
    career_injuries: float
    career_severity: float
    missed_prev_year: float
    current_year: int = 2024

@app.get("/")
def root():
    return {"status": "MLB Career Predictor API is running"}

@app.post("/predict")
def predict(player: PlayerInput):
    features = [[
        player.age, player.wOBA, player.lag_wOBA, player.lag_PA,
        player.career_PA, player.career_G, player.years_in_league,
        player.total_injuries, player.avg_severity, player.career_injuries,
        player.career_severity, player.missed_prev_year
    ]]
    prediction = float(model.predict(features)[0])
    prediction = max(0, round(prediction, 1))
    return {
        "prediction": prediction,
        "estimated_final_season": int(player.current_year + prediction),
        "unit": "years"
    }

@app.get("/player/{first_name}/{last_name}")
def get_player(first_name: str, last_name: str):
    first = first_name.lower().strip()
    last = last_name.lower().strip()

    player_df = df[
        (df["nameFirst"] == first) &
        (df["nameLast"] == last)
    ].sort_values("yearID")

    if len(player_df) == 0:
        raise HTTPException(status_code=404, detail="Player not found")

    # Get latest season for prediction
    latest = player_df.iloc[-1]
    features = [[
        latest["age"], latest["wOBA"], latest["lag_wOBA"], latest["lag_PA"],
        latest["career_PA"], latest["career_G"], latest["years_in_league"],
        latest["total_injuries"], latest["avg_severity"], latest["career_injuries"],
        latest["career_severity"], latest["missed_prev_year"]
    ]]

    prediction = float(model.predict(features)[0])
    prediction = max(0, round(prediction, 1))

    # Build career history for plotting
    career_history = player_df[["yearID", "age", "wOBA", "career_PA", "career_injuries"]].to_dict(orient="records")

    return {
        "playerID": latest["playerID"],
        "nameFirst": latest["nameFirst"],
        "nameLast": latest["nameLast"],
        "seasons_played": len(player_df),
        "latest_season": int(latest["yearID"]),
        "latest_age": float(latest["age"]),
        "prediction": prediction,
        "estimated_final_season": int(latest["yearID"] + prediction),
        "career_history": career_history
    }

@app.get("/search/{last_name}")
def search_players(last_name: str):
    last = last_name.lower().strip()
    matches = df[df["nameLast"] == last][["playerID", "nameFirst", "nameLast"]].drop_duplicates()
    if len(matches) == 0:
        raise HTTPException(status_code=404, detail="No players found")
    return {"players": matches.to_dict(orient="records")}
