import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Recovery Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SLIDE_DURATION_MS = 15_000   # 15 seconden per slide — pas dit aan naar wens
count = st_autorefresh(interval=SLIDE_DURATION_MS, limit=None, key="tv")

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0d1117 !important; }
  [data-testid="stHeader"]           { display: none !important; }
  [data-testid="stSidebar"]          { display: none !important; }
  footer                             { display: none !important; }
  .block-container { padding: 1.4rem 2.2rem 0.5rem 2.2rem; max-width: 100%; }
  .slide-title    { font-size: 2.8rem; font-weight: 800; letter-spacing: 0.03em; color: #f1f5f9; }
  .slide-subtitle { font-size: 1.2rem; color: #64748b; margin-top: 0.1rem; margin-bottom: 1.4rem; }
  .clock          { font-size: 1.05rem; color: #475569; text-align: right; margin-bottom: -1rem; }
  .person-card {
      background: #1e293b; border: 1px solid #334155;
      border-radius: 20px; padding: 1.6rem; height: 100%;
  }
  .person-name  { font-size: 1.45rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.8rem; }
  .metric-card  { background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 1rem 1.3rem; margin-bottom: 0.7rem; }
  .metric-label { font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; }
  .metric-value { font-size: 2.3rem; font-weight: 700; margin-top: 0.1rem; }
  .green  { color: #22c55e !important; }
  .yellow { color: #f59e0b !important; }
  .red    { color: #ef4444 !important; }
  .blue   { color: #38bdf8 !important; }
  .prog-bg   { background: #334155; border-radius: 999px; height: 13px; margin: 0.45rem 0 0.9rem 0; }
  .prog-fill { border-radius: 999px; height: 13px; }
  .row-between { display: flex; justify-content: space-between; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load():
    team   = pd.read_csv("data/team_data.csv")
    budget = pd.read_csv("data/budget.csv")
    return team, budget

team_df, budget_df = load()

def recovery_color(pct):
    if pct >= 80:  return "#22c55e"
    if pct >= 50:  return "#f59e0b"
    return "#ef4444"

def progress_bar(pct, color):
    pct = min(max(pct, 0), 100)
    return f'<div class="prog-bg"><div class="prog-fill" style="width:{pct:.1f}%;background:{color};"></div></div>'

def fmt(val, unit="EUR"):
    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    if unit in symbols:
        return f"{symbols[unit]}{val:,.0f}"
    return f"{val:,.0f} {unit}"

n_people     = len(team_df)
total_slides = n_people + 2
slide_idx    = count % total_slides
now_str      = datetime.now().strftime("%A, %d %b %Y  •  %H:%M")

if slide_idx == 0:
    st.markdown(f'<div class="clock">{now_str}</div>', unsafe_allow_html=True)
    st.markdown('<div class="slide-title">🏆 Team Recovery Overzicht</div>', unsafe_allow_html=True)
    st.markdown('<div class="slide-subtitle">Commercieel verlies recovery · Alle medewerkers</div>', unsafe_allow_html=True)

    cols = st.columns(min(n_people, 4))
    for i, row in team_df.iterrows():
        initial   = float(row["initial_loss"])
        recovered = float(row["recovered"])
        target    = float(row["recovery_target"])
        pending   = int(row["pending_cases"])
        unit      = str(row.get("currency", "EUR"))
        to_go     = max(target - recovered, 0)
        pct       = (recovered / target * 100) if target > 0 else 0
        color     = recovery_color(pct)
        bar       = progress_bar(pct, color)

        with cols[i % min(n_people, 4)]:
            st.markdown(f"""
            <div class="person-card">
              <div class="person-name">{row['name']}</div>
              <div class="metric-label">Recovery voortgang</div>
              {bar}
              <span style="color:{color}; font-size:1.6rem; font-weight:700;">{pct:.0f}%</span>
              <hr style="border:none; border-top:1px solid #334155; margin:0.9rem 0;">
              <div class="row-between">
                <span class="metric-label">Initieel verlies</span>
                <span style="color:#ef4444; font-weight:600;">{fmt(initial, unit)}</span>
              </div>
              <div class="row-between">
                <span class="metric-label">Hersteld ✅</span>
                <span style="color:#22c55e; font-weight:600;">{fmt(recovered, unit)}</span>
              </div>
              <div class="row-between">
                <span class="metric-label">Nog te herstellen ⏳</span>
                <span style="color:#f59e0b; font-weight:600;">{fmt(to_go, unit)}</span>
              </div>
              <div class="row-between" style="margin-bottom:0;">
                <span class="metric-label">Openstaande dossiers 📁</span>
                <span style="color:#38bdf8; font-weight:600;">{pending}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

elif 1 <= slide_idx <= n_people:
    p         = team_df.iloc[slide_idx - 1]
    initial   = float(p["initial_loss"])
    recovered = float(p["recovered"])
    target    = float(p["recovery_target"])
    pending   = int(p["pending_cases"])
    unit      = str(p.get("currency", "EUR"))
    to_go     = max(target - recovered, 0)
    pct       = (recovered / target * 100) if target > 0 else 0
    color     = recovery_color(pct)

    st.markdown(f'<div class="clock">{now_str}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="slide-title">👤 {p["name"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="slide-subtitle">Individuele recovery breakdown</div>', unsafe_allow_html=True)

    left, right = st.columns([1.3, 1])

    with left:
        fig = go.Figure(go.Indicator(
            mode  = "gauge+number+delta",
            value = pct,
            delta = {"reference": 80, "suffix": "%", "font": {"size": 28}},
            number= {"suffix": "%", "font": {"size": 72, "color": "white"}},
            gauge = {
                "axis"       : {"range": [0, 100], "tickfont": {"color": "#94a3b8", "size": 16}},
                "bar"        : {"color": color, "thickness": 0.28},
                "bgcolor"    : "#1e293b",
                "bordercolor": "#334155",
                "steps"      : [{"range": [0, 100], "color": "#1e293b"}],
                "threshold"  : {"line": {"color": "#f1f5f9", "width": 3}, "thickness": 0.75, "value": 80},
            },
            title = {"text": "Recovery Rate", "font": {"size": 22, "color": "#64748b"}},
        ))
        fig.update_layout(
            paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
            font_color="white", height=420,
            margin=dict(l=50, r=50, t=60, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("<br>", unsafe_allow_html=True)
        for label, value, cls in [
            ("💸 Initieel verlies",      fmt(initial,   unit), "red"),
            ("✅ Al hersteld",           fmt(recovered,  unit), "green"),
            ("⏳ Nog te herstellen",     fmt(to_go,      unit), "yellow"),
            ("📁 Openstaande dossiers",  str(pending),          "blue"),
        ]:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value {cls}">{value}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown(f'<div class="clock">{now_str}</div>', unsafe_allow_html=True)
    st.markdown('<div class="slide-title">🎯 Budget & Teamdoelen</div>', unsafe_allow_html=True)
    st.markdown("<div class=\"slide-subtitle\">Doelstellingen van het management deze maand</div>", unsafe_allow_html=True)

    cols = st.columns(min(len(budget_df), 3))
    for i, row in budget_df.iterrows():
        current  = float(row["current_value"])
        target_v = float(row["target_value"])
        unit     = str(row["unit"])
        note     = str(row.get("note", ""))
        pct      = (current / target_v * 100) if target_v > 0 else 0
        color    = recovery_color(pct)
        bar      = progress_bar(pct, color)

        with cols[i % min(len(budget_df), 3)]:
            st.markdown(f"""
            <div class="person-card">
              <div class="metric-label" style="font-size:1rem; margin-bottom:0.5rem;">{row['metric']}</div>
              <div style="color:{color}; font-size:2.4rem; font-weight:700;">{fmt(current, unit)}</div>
              <div style="color:#475569; font-size:0.95rem; margin:0.3rem 0 0.2rem 0;">
                Doel: <span style="color:#94a3b8;">{fmt(target_v, unit)}</span>
              </div>
              {bar}
              <span style="color:{color}; font-size:1.25rem; font-weight:700;">{pct:.0f}% behaald</span>
              {"<div style='color:#64748b; font-size:0.9rem; margin-top:0.6rem;'>" + note + "</div>" if note and note != "nan" else ""}
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
dots = ""
for i in range(total_slides):
    if i == slide_idx:
        style = "background:#38bdf8; width:28px; height:10px;"
    else:
        style = "background:#334155; width:10px; height:10px;"
    dots += f'<div style="{style} border-radius:999px; margin:0 4px; display:inline-block;"></div>'
st.markdown(f'<div style="text-align:center; margin-top:0.4rem;">{dots}</div>', unsafe_allow_html=True)
