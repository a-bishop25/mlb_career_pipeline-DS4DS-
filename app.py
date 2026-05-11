import streamlit as st
import requests
import plotly.graph_objects as go

API_URL = "http://54.210.153.26:8000"

st.set_page_config(
    page_title="MLB Career Longevity Predictor",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Bebas+Neue&family=Source+Serif+4:ital,wght@0,300;0,600;1,300&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background-color: #0a1628;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(185,28,28,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(29,78,140,0.15) 0%, transparent 60%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.015'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    font-family: 'Source Serif 4', Georgia, serif;
    color: #f5f0e8;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #0a1628 0%, #1a2a4a 40%, #0a1628 100%);
    border-bottom: 3px solid #c41e3a;
    padding: 3rem 4rem 2rem;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 120%;
    height: 200%;
    background: repeating-linear-gradient(
        -45deg,
        transparent,
        transparent 40px,
        rgba(196,30,58,0.03) 40px,
        rgba(196,30,58,0.03) 41px
    );
    pointer-events: none;
}

.hero-eyebrow {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.4em;
    color: #c41e3a;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    font-weight: 900;
    color: #f5f0e8;
    line-height: 1.05;
    margin-bottom: 0.75rem;
    text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}

.hero-title span { color: #c41e3a; }

.hero-subtitle {
    font-family: 'Source Serif 4', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #a0aec0;
    max-width: 600px;
    line-height: 1.6;
}

.hero-badge {
    display: inline-block;
    background: rgba(196,30,58,0.15);
    border: 1px solid rgba(196,30,58,0.4);
    color: #f87171;
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 0.15em;
    font-size: 0.75rem;
    padding: 0.25rem 0.75rem;
    border-radius: 2px;
    margin-top: 1rem;
}

/* ── Search Section ── */
.search-section {
    background: #0d1f3c;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 2rem 4rem;
}

.search-label {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 0.2em;
    font-size: 0.8rem;
    color: #c41e3a;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

/* ── Streamlit input overrides ── */
.stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 3px !important;
    color: #f5f0e8 !important;
    font-family: 'Source Serif 4', serif !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput input:focus {
    border-color: #c41e3a !important;
    box-shadow: 0 0 0 2px rgba(196,30,58,0.2) !important;
}

.stTextInput label {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 0.15em !important;
    font-size: 0.8rem !important;
    color: #a0aec0 !important;
}

.stButton button {
    background: #c41e3a !important;
    color: #ffffff !important;
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 0.2em !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton button:hover {
    background: #a01830 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(196,30,58,0.4) !important;
}

/* ── Player Card ── */
.player-card {
    background: linear-gradient(135deg, #1a2a4a 0%, #0d1f3c 100%);
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 4px solid #c41e3a;
    border-radius: 4px;
    padding: 2.5rem 4rem;
    margin: 0;
    position: relative;
    overflow: hidden;
}

.player-card::after {
    content: '⚾';
    position: absolute;
    right: 3rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 8rem;
    opacity: 0.04;
    pointer-events: none;
}

.player-name {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 4vw, 3.5rem);
    font-weight: 900;
    color: #f5f0e8;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.player-meta {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 0.25em;
    font-size: 0.8rem;
    color: #c41e3a;
    margin-bottom: 1.5rem;
}

/* ── Stat boxes (vintage card style) ── */
.stat-grid {
    display: flex;
    gap: 1px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.stat-box {
    flex: 1;
    background: #0a1628;
    padding: 1rem 1.25rem;
    text-align: center;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.stat-box:last-child { border-right: none; }

.stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #f5f0e8;
    line-height: 1;
    display: block;
}

.stat-value.highlight { color: #c41e3a; }

.stat-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #6b7a99;
    text-transform: uppercase;
    margin-top: 0.25rem;
    display: block;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 2rem 4rem 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}

.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f5f0e8;
}

.section-rule {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(196,30,58,0.5), transparent);
}

/* ── Prediction verdict ── */
.verdict {
    border-radius: 3px;
    padding: 1.5rem 2rem;
    margin: 0 4rem 2rem;
    border-left: 4px solid;
}

.verdict.elite {
    background: rgba(34,197,94,0.08);
    border-color: #22c55e;
    color: #86efac;
}

.verdict.solid {
    background: rgba(59,130,246,0.08);
    border-color: #3b82f6;
    color: #93c5fd;
}

.verdict.limited {
    background: rgba(234,179,8,0.08);
    border-color: #eab308;
    color: #fde047;
}

.verdict.ending {
    background: rgba(196,30,58,0.08);
    border-color: #c41e3a;
    color: #fca5a5;
}

.verdict-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 0.15em;
    margin-bottom: 0.25rem;
}

.verdict-body {
    font-family: 'Source Serif 4', serif;
    font-style: italic;
    font-size: 0.95rem;
    opacity: 0.9;
}

/* ── Charts padding ── */
.chart-wrap {
    padding: 0 4rem 2rem;
}

/* ── Footer ── */
.footer {
    background: #060e1c;
    border-top: 1px solid rgba(255,255,255,0.06);
    padding: 1.5rem 4rem;
    text-align: center;
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 0.15em;
    font-size: 0.7rem;
    color: #3d4f6e;
}

/* ── Spinner ── */
.stSpinner { color: #c41e3a !important; }

/* ── Divider hide ── */
hr { display: none !important; }

/* ── Plotly transparent bg fix ── */
.js-plotly-plot { border-radius: 4px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Advanced Analytics · Machine Learning · Career Intelligence</div>
    <div class="hero-title">MLB Career<br><span>Longevity</span> Predictor</div>
    <div class="hero-subtitle">Enter any MLB position player to see their full career trajectory, performance arc, and data-driven projection of years remaining.</div>
    <div class="hero-badge">⚾ Powered by Random Forest · Trained on 60,000+ Player Seasons</div>
</div>
""", unsafe_allow_html=True)

# ── Search ────────────────────────────────────────────────
st.markdown('<div class="search-section">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    first_name = st.text_input("FIRST NAME", placeholder="e.g. mike")
with col2:
    last_name = st.text_input("LAST NAME", placeholder="e.g. trout")
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    search = st.button("SEARCH PLAYER", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    plot_bgcolor="#0a1628",
    paper_bgcolor="#0d1f3c",
    font=dict(color="#a0aec0", family="Source Serif 4, serif"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    margin=dict(t=40, b=40, l=50, r=30),
    hoverlabel=dict(bgcolor="#1a2a4a", font_color="#f5f0e8", font_family="Source Serif 4, serif")
)

if search and first_name and last_name:
    with st.spinner(f"Pulling career file for {first_name.title()} {last_name.title()}..."):
        try:
            response = requests.get(
                f"{API_URL}/player/{first_name.lower().strip()}/{last_name.lower().strip()}",
                timeout=30
            )
            if response.status_code == 404:
                st.error("Player not found. Check spelling — names are case-insensitive.")
                st.stop()

            data = response.json()
            career = data["career_history"]
            name = f"{data['nameFirst'].title()} {data['nameLast'].title()}"
            prediction = data["prediction"]
            years = [r["yearID"] for r in career]
            wobas = [r["wOBA"] for r in career]
            injuries = [r["career_injuries"] for r in career]
            avg_woba = round(sum(wobas) / len(wobas), 3)

            # ── Player Card ───────────────────────────────
            st.markdown(f"""
            <div class="player-card">
                <div class="player-name">{name}</div>
                <div class="player-meta">MLB Position Player · Career Profile · {data['latest_season']} Last Recorded Season</div>
                <div class="stat-grid">
                    <div class="stat-box">
                        <span class="stat-value">{data['seasons_played']}</span>
                        <span class="stat-label">Seasons</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-value">{int(data['latest_age'])}</span>
                        <span class="stat-label">Age (Last Season)</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-value">{avg_woba}</span>
                        <span class="stat-label">Career Avg wOBA</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-value highlight">{prediction}</span>
                        <span class="stat-label">Yrs Remaining</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-value">{data['estimated_final_season']}</span>
                        <span class="stat-label">Est. Final Season</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Verdict ───────────────────────────────────
            if prediction >= 8:
                vclass, vtitle, vbody = "elite", "Elite Longevity Profile", f"{name} projects as a long-tenured MLB player with an estimated {prediction} years remaining — a rare career durability profile."
            elif prediction >= 4:
                vclass, vtitle, vbody = "solid", "Solid Career Runway", f"{name} has meaningful years ahead, projecting to play until approximately {data['estimated_final_season']}."
            elif prediction >= 2:
                vclass, vtitle, vbody = "limited", "Limited Years Remaining", f"{name} is in the final chapter of their career, with an estimated {prediction} seasons left."
            else:
                vclass, vtitle, vbody = "ending", "Career Nearing Its End", f"The model projects {name} has fewer than 2 seasons remaining based on their performance and injury profile."

            st.markdown(f"""
            <div class="verdict {vclass}">
                <div class="verdict-title">{vtitle}</div>
                <div class="verdict-body">{vbody}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── wOBA Trajectory ───────────────────────────
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Performance Trajectory</div>
                <div class="section-rule"></div>
            </div>
            """, unsafe_allow_html=True)

            last_woba = wobas[-1]
            last_year = data["latest_season"]
            future_years = list(range(last_year + 1, last_year + int(prediction) + 2))
            future_wobas = [max(0.200, last_woba - (i * 0.008)) for i in range(1, len(future_years) + 1)]

            fig1 = go.Figure()
            fig1.add_hline(y=avg_woba, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                          annotation_text=f"Career Avg {avg_woba}", annotation_font_color="#6b7a99")
            fig1.add_trace(go.Scatter(
                x=years, y=wobas, mode="lines+markers", name="Actual wOBA",
                line=dict(color="#c41e3a", width=2.5),
                marker=dict(size=7, color="#c41e3a", line=dict(color="#f5f0e8", width=1)),
                hovertemplate="<b>%{x}</b><br>wOBA: %{y:.3f}<extra></extra>"
            ))
            fig1.add_trace(go.Scatter(
                x=[last_year] + future_years, y=[last_woba] + future_wobas,
                mode="lines+markers", name="Projected",
                line=dict(color="#f59e0b", width=2, dash="dot"),
                marker=dict(size=5, color="#f59e0b", symbol="diamond"),
                hovertemplate="<b>%{x}</b><br>Projected wOBA: %{y:.3f}<extra></extra>"
            ))
            layout1 = {**PLOT_LAYOUT, "height": 380, "legend": dict(
                orientation="h", yanchor="bottom", y=1.02,
                font=dict(color="#a0aec0")
            )}
            fig1.update_layout(**layout1)
            fig1.update_xaxes(title_text="Season", title_font_color="#6b7a99")
            fig1.update_yaxes(title_text="wOBA", title_font_color="#6b7a99")

            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Survival + Gauge side by side ─────────────
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Career Survival Projection</div>
                <div class="section-rule"></div>
            </div>
            """, unsafe_allow_html=True)

            surv_col1, surv_col2 = st.columns([3, 2])

            with surv_col1:
                survival_years = list(range(0, 16))
                survival_probs = [max(0, 100 * (1 - (i / (prediction + 0.001)) ** 1.5)) for i in survival_years]

                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=survival_years, y=survival_probs,
                    mode="lines", fill="tozeroy", name="Survival Probability",
                    line=dict(color="#22c55e", width=2.5),
                    fillcolor="rgba(34,197,94,0.08)",
                    hovertemplate="<b>%{x} years from now</b><br>Probability: %{y:.1f}%<extra></extra>"
                ))
                layout2 = {**PLOT_LAYOUT, "height": 320}
                fig2.update_layout(**layout2)
                fig2.update_xaxes(title_text="Years From Now", title_font_color="#6b7a99")
                fig2.update_yaxes(title_text="Probability Still Active (%)", title_font_color="#6b7a99", range=[0, 105])
                st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

            with surv_col2:
                fig3 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=prediction,
                    number={"suffix": " yrs", "font": {"color": "#f5f0e8", "size": 36, "family": "Bebas Neue"}},
                    title={"text": "YEARS REMAINING", "font": {"color": "#6b7a99", "size": 11, "family": "Bebas Neue"}},
                    gauge={
                        "axis": {"range": [0, 20], "tickcolor": "#6b7a99", "tickfont": {"color": "#6b7a99"}},
                        "bar": {"color": "#c41e3a", "thickness": 0.25},
                        "bgcolor": "#0a1628",
                        "bordercolor": "rgba(255,255,255,0.1)",
                        "steps": [
                            {"range": [0, 3], "color": "rgba(196,30,58,0.15)"},
                            {"range": [3, 7], "color": "rgba(234,179,8,0.1)"},
                            {"range": [7, 20], "color": "rgba(34,197,94,0.1)"},
                        ],
                    }
                ))
                fig3.update_layout(
                    height=320,
                    paper_bgcolor="#0d1f3c",
                    plot_bgcolor="#0d1f3c",
                    margin=dict(t=60, b=20, l=30, r=30),
                    font=dict(color="#a0aec0")
                )
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

            # ── Injury Timeline ───────────────────────────
            st.markdown("""
            <div class="section-header">
                <div class="section-title">Injury Accumulation</div>
                <div class="section-rule"></div>
            </div>
            """, unsafe_allow_html=True)

            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                x=years, y=injuries, name="Cumulative Injuries",
                marker=dict(
                    color=injuries,
                    colorscale=[[0, "rgba(196,30,58,0.3)"], [1, "#c41e3a"]],
                    line=dict(color="rgba(255,255,255,0.05)", width=0.5)
                ),
                hovertemplate="<b>%{x}</b><br>Career Injuries: %{y}<extra></extra>"
            ))
            layout4 = {**PLOT_LAYOUT, "height": 280, "showlegend": False}
            fig4.update_layout(**layout4)
            fig4.update_xaxes(title_text="Season", title_font_color="#6b7a99")
            fig4.update_yaxes(title_text="Cumulative Career Injuries", title_font_color="#6b7a99")

            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"API Error: {e}")

elif search:
    st.warning("Please enter both first and last name.")

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Random Forest Regressor &nbsp;·&nbsp; MAE 2.53 Years &nbsp;·&nbsp; R² 0.363 &nbsp;·&nbsp;
    Pipeline: S3 → Databricks Spark → MLflow → EC2 FastAPI &nbsp;·&nbsp;
    Trained on 47,991 MLB Player Seasons
</div>
""", unsafe_allow_html=True)
