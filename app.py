import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

API_URL = "http://54.210.153.26:8000"

st.set_page_config(
    page_title="MLB Career Longevity Predictor",
    page_icon="⚾",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTitle { color: #ffffff; font-size: 3rem; }
    .metric-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚾ MLB Career Longevity Predictor")
st.markdown("Search any MLB position player to see their career trajectory and projected years remaining.")

# ── Player Search ─────────────────────────────────────────
st.subheader("Player Search")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    first_name = st.text_input("First Name", placeholder="e.g. mike")
with col2:
    last_name = st.text_input("Last Name", placeholder="e.g. trout")
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("🔍 Search", use_container_width=True)

if search and first_name and last_name:
    with st.spinner(f"Loading {first_name.title()} {last_name.title()}'s career data..."):
        try:
            response = requests.get(
                f"{API_URL}/player/{first_name.lower().strip()}/{last_name.lower().strip()}",
                timeout=30
            )

            if response.status_code == 404:
                st.error("Player not found. Check spelling and try again.")
                st.stop()

            data = response.json()
            career = data["career_history"]

            # ── Player Header ─────────────────────────────
            st.divider()
            name = f"{data['nameFirst'].title()} {data['nameLast'].title()}"
            st.header(f"⚾ {name}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Seasons Played", data["seasons_played"])
            with col2:
                st.metric("Latest Season", data["latest_season"])
            with col3:
                st.metric("Current Age", int(data["latest_age"]))
            with col4:
                st.metric("Predicted Years Remaining", f"{data['prediction']}")

            # ── Career wOBA Trajectory ─────────────────────
            st.divider()
            st.subheader("Career Performance Trajectory")

            years = [r["yearID"] for r in career]
            wobas = [r["wOBA"] for r in career]
            ages = [r["age"] for r in career]

            # Project future seasons
            prediction = data["prediction"]
            last_year = data["latest_season"]
            last_woba = wobas[-1]
            avg_woba = sum(wobas) / len(wobas)

            future_years = list(range(last_year + 1, last_year + int(prediction) + 2))
            future_wobas = [
                max(0.200, last_woba - (i * 0.008))
                for i in range(1, len(future_years) + 1)
            ]

            fig = go.Figure()

            # Actual career line
            fig.add_trace(go.Scatter(
                x=years,
                y=wobas,
                mode="lines+markers",
                name="Actual wOBA",
                line=dict(color="#1f77b4", width=3),
                marker=dict(size=8),
                hovertemplate="Year: %{x}<br>wOBA: %{y:.3f}<extra></extra>"
            ))

            # Career average line
            fig.add_hline(
                y=avg_woba,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"Career Avg: {avg_woba:.3f}"
            )

            # Projected career line
            fig.add_trace(go.Scatter(
                x=[last_year] + future_years,
                y=[last_woba] + future_wobas,
                mode="lines+markers",
                name="Projected wOBA",
                line=dict(color="#ff7f0e", width=2, dash="dot"),
                marker=dict(size=6, symbol="diamond"),
                hovertemplate="Year: %{x}<br>Projected wOBA: %{y:.3f}<extra></extra>"
            ))

            fig.update_layout(
                xaxis_title="Season",
                yaxis_title="wOBA",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                plot_bgcolor="#1e2130",
                paper_bgcolor="#0e1117",
                font=dict(color="white"),
                xaxis=dict(gridcolor="#2a2d3e"),
                yaxis=dict(gridcolor="#2a2d3e")
            )

            st.plotly_chart(fig, use_container_width=True)

            # ── Survival Curve ────────────────────────────
            st.subheader("Career Survival Probability")

            survival_years = list(range(0, 16))
            survival_probs = [
                max(0, 100 * (1 - (i / (prediction + 0.001)) ** 1.5))
                for i in survival_years
            ]

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=survival_years,
                y=survival_probs,
                mode="lines",
                fill="tozeroy",
                name="Survival Probability",
                line=dict(color="#2ca02c", width=3),
                fillcolor="rgba(44, 160, 44, 0.2)",
                hovertemplate="Years from now: %{x}<br>Probability: %{y:.1f}%<extra></extra>"
            ))

            fig2.update_layout(
                xaxis_title="Years From Now",
                yaxis_title="Probability of Still Playing (%)",
                height=350,
                plot_bgcolor="#1e2130",
                paper_bgcolor="#0e1117",
                font=dict(color="white"),
                xaxis=dict(gridcolor="#2a2d3e"),
                yaxis=dict(gridcolor="#2a2d3e", range=[0, 105])
            )

            st.plotly_chart(fig2, use_container_width=True)

            # ── Injury History ────────────────────────────
            st.subheader("Injury History by Season")

            injuries = [r["career_injuries"] for r in career]

            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=years,
                y=injuries,
                name="Career Injuries",
                marker_color="#d62728",
                hovertemplate="Year: %{x}<br>Career Injuries: %{y}<extra></extra>"
            ))

            fig3.update_layout(
                xaxis_title="Season",
                yaxis_title="Cumulative Career Injuries",
                height=300,
                plot_bgcolor="#1e2130",
                paper_bgcolor="#0e1117",
                font=dict(color="white"),
                xaxis=dict(gridcolor="#2a2d3e"),
                yaxis=dict(gridcolor="#2a2d3e")
            )

            st.plotly_chart(fig3, use_container_width=True)

            # ── Prediction Summary ────────────────────────
            st.divider()
            st.subheader("Career Longevity Prediction")

            pred_col1, pred_col2 = st.columns(2)

            with pred_col1:
                fig4 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=data["prediction"],
                    title={"text": "Predicted Years Remaining", "font": {"color": "white"}},
                    number={"font": {"color": "white"}},
                    gauge={
                        "axis": {"range": [0, 20], "tickcolor": "white"},
                        "bar": {"color": "#1f77b4"},
                        "bgcolor": "#1e2130",
                        "steps": [
                            {"range": [0, 3], "color": "#ff4444"},
                            {"range": [3, 7], "color": "#ffaa00"},
                            {"range": [7, 20], "color": "#44bb44"},
                        ],
                    }
                ))
                fig4.update_layout(
                    height=300,
                    paper_bgcolor="#0e1117",
                    font=dict(color="white")
                )
                st.plotly_chart(fig4, use_container_width=True)

            with pred_col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if data["prediction"] >= 8:
                    st.success(f"🟢 **Elite Longevity Profile** — {name} projects to play until approximately **{data['estimated_final_season']}**")
                elif data["prediction"] >= 4:
                    st.info(f"🔵 **Solid Career Runway** — {name} projects to play until approximately **{data['estimated_final_season']}**")
                elif data["prediction"] >= 2:
                    st.warning(f"🟡 **Limited Years Remaining** — {name} projects to play until approximately **{data['estimated_final_season']}**")
                else:
                    st.error(f"🔴 **Career Nearing End** — {name} may have only **{data['prediction']} years** remaining")

                st.markdown(f"""
                - **Seasons in dataset:** {data['seasons_played']}
                - **Last recorded season:** {data['latest_season']}
                - **Age at last season:** {int(data['latest_age'])}
                - **Estimated final season:** {data['estimated_final_season']}
                """)

        except Exception as e:
            st.error(f"Error: {e}")

elif search:
    st.warning("Please enter both first and last name.")

# ── Footer ────────────────────────────────────────────────
st.divider()
st.caption("Model: Random Forest Regressor | MAE: ~2.53 years | R²: 0.363 | Pipeline: S3 → Databricks Spark → MLflow → EC2 FastAPI")
