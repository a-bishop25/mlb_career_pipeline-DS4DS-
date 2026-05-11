import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = "http://54.210.153.26:8000/predict"

st.set_page_config(
    page_title="MLB Career Longevity Predictor",
    page_icon="⚾",
    layout="wide"
)

st.title("⚾ MLB Career Longevity Predictor")
st.markdown("Enter a player's current season stats and injury history to predict how many years they have left in their MLB career.")

st.subheader("Player Stats")
col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=18, max_value=45, value=27)
    wOBA = st.number_input("wOBA (this season)", min_value=0.0, max_value=0.600, value=0.320, step=0.001, format="%.3f")
    lag_wOBA = st.number_input("wOBA (last season)", min_value=0.0, max_value=0.600, value=0.315, step=0.001, format="%.3f")
    lag_PA = st.number_input("Plate Appearances (last season)", min_value=0, max_value=800, value=450)

with col2:
    career_PA = st.number_input("Career Plate Appearances", min_value=0, max_value=15000, value=2000)
    career_G = st.number_input("Career Games Played", min_value=0, max_value=3500, value=500)
    years_in_league = st.number_input("Years in League", min_value=0, max_value=30, value=3)

with col3:
    total_injuries = st.number_input("Injuries This Season", min_value=0, max_value=20, value=0)
    avg_severity = st.number_input("Avg Injury Severity (0-10)", min_value=0.0, max_value=10.0, value=0.0, step=0.1)
    career_injuries = st.number_input("Career Total Injuries", min_value=0, max_value=50, value=2)
    career_severity = st.number_input("Career Total Severity", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
    missed_prev_year = st.number_input("Missed Previous Year? (0=No, 1=Yes)", min_value=0, max_value=1, value=0)

if st.button("🔮 Predict Career Longevity", use_container_width=True):
    payload = {
        "age": age,
        "wOBA": wOBA,
        "lag_wOBA": lag_wOBA,
        "lag_PA": lag_PA,
        "career_PA": career_PA,
        "career_G": career_G,
        "years_in_league": years_in_league,
        "total_injuries": total_injuries,
        "avg_severity": avg_severity,
        "career_injuries": career_injuries,
        "career_severity": career_severity,
        "missed_prev_year": missed_prev_year
    }

    with st.spinner("Predicting..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=30)
            result = response.json()

            prediction = result["prediction"]
            final_season = result["estimated_final_season"]

            st.divider()
            st.subheader("Prediction Results")

            res_col1, res_col2 = st.columns(2)

            with res_col1:
                st.metric(
                    label="Predicted Years Remaining",
                    value=f"{prediction} years",
                    delta=f"Estimated final season: {final_season}"
                )

                if prediction >= 8:
                    st.success("Long career ahead — elite longevity profile")
                elif prediction >= 4:
                    st.info("Solid career runway remaining")
                elif prediction >= 2:
                    st.warning("Limited years remaining — key decision window")
                else:
                    st.error("Career may be nearing its end")

            with res_col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prediction,
                    title={"text": "Years Remaining"},
                    gauge={
                        "axis": {"range": [0, 20]},
                        "bar": {"color": "#1f77b4"},
                        "steps": [
                            {"range": [0, 3], "color": "#ff4444"},
                            {"range": [3, 7], "color": "#ffaa00"},
                            {"range": [7, 20], "color": "#44bb44"},
                        ],
                    }
                ))
                fig.update_layout(height=300, margin=dict(t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error connecting to prediction API: {e}")

st.divider()
st.caption("Model: Random Forest Regressor | MAE: ~2.53 years | R²: 0.363 | Trained on MLB position player data | Pipeline: S3 → Databricks → MLflow → EC2 FastAPI")