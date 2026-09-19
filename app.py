import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, PULP_CBC_CMD

# Configure Page
st.set_page_config(
    page_title="IPL Decision Intelligence HUD",
    page_icon="🏏",
    layout="wide"
)

# Broadcast Cyberpunk Styling
st.markdown("""
<style>
    .stApp { background-color: #070d12; color: #d8f6f7; }
    div[data-testid="stMetricValue"] { color: #00f2fe !important; font-family: monospace; }
    .stSelectbox label, .stSlider label { color: #00f2fe !important; font-weight: bold; }
    h1, h2, h3 { color: #00f2fe !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    pool = pd.read_csv("ipl_auction_valuations_2026.csv")
    bat = pd.read_csv("ipl_phase_batting_metrics.csv")
    bowl = pd.read_csv("ipl_phase_bowling_metrics.csv")
    return pool, bat, bowl

player_pool, bat_phase, bowl_phase = load_data()

st.title("⚡ IPL DECISION INTELLIGENCE COMMAND HUD")
st.caption("Phase Decomposer • MILP Squad Optimization • Algorithmic Valuations")

tab1, tab2 = st.tabs(["🔍 Player Scouting Dossier", "💰 Best Playing XI Solver"])

# --- TAB 1: PLAYER SCOUTING ---
with tab1:
    target_player = st.selectbox("Select Target Player:", sorted(player_pool['player_name'].unique()))
    p_data = player_pool[player_pool['player_name'] == target_player].iloc[0]
    p_bat = bat_phase[bat_phase['striker'] == target_player]
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tactical Role", str(p_data['role']))
    col2.metric("Est. Auction Value", f"₹ {p_data['est_price_cr']:.2f} Cr")
    col3.metric("Impact Score", f"{p_data['impact_score']:.1f}")
    col4.metric("Career Volume", f"{int(p_data['total_runs'])} R / {int(p_data['total_wickets'])} W")

    tsr_pp = float(p_bat[p_bat['phase'] == 'Powerplay']['true_strike_rate'].values[0]) if not p_bat[p_bat['phase'] == 'Powerplay'].empty else 0.0
    tsr_mid = float(p_bat[p_bat['phase'] == 'Middle']['true_strike_rate'].values[0]) if not p_bat[p_bat['phase'] == 'Middle'].empty else 0.0
    tsr_dth = float(p_bat[p_bat['phase'] == 'Death']['true_strike_rate'].values[0]) if not p_bat[p_bat['phase'] == 'Death'].empty else 0.0

    radar_vals = [
        min(max(tsr_pp + 50, 10), 100),
        min(max(tsr_mid + 50, 10), 100),
        min(max(tsr_dth + 50, 10), 100),
        min(max((int(p_data['total_runs']) / 6000) * 100, 15), 100),
        min(max((int(p_data['total_wickets']) / 160) * 100, 10), 100)
    ]

    fig = go.Figure(data=go.Scatterpolar(
        r=radar_vals,
        theta=['Powerplay TSR', 'Middle TSR', 'Death TSR', 'Run Volume', 'Wicket Threat'],
        fill='toself',
        fillcolor='rgba(0, 242, 254, 0.25)',
        line=dict(color='#00f2fe', width=2)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#1a3344'), bgcolor='#070d12'),
        paper_bgcolor='#070d12',
        font=dict(color='#d8f6f7'),
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: BEST PLAYING XI SOLVER ---
with tab2:
    st.subheader("Mixed-Integer Linear Programming Squad Allocation")
    budget = st.slider("Franchise Purse Cap (₹ Cr):", min_value=50.0, max_value=100.0, value=75.0, step=2.5)
    
    if st.button("⚡ Solve Optimal Playing XI"):
        prob = LpProblem("Best_XI", LpMaximize)
        players = player_pool['player_name'].tolist()
        scores = dict(zip(players, player_pool['impact_score']))
        costs = dict(zip(players, player_pool['est_price_cr']))
        roles = dict(zip(players, player_pool['role']))

        x = {p: LpVariable(f"xi_{i}", cat="Binary") for i, p in enumerate(players)}

        prob += lpSum([x[p] * scores[p] for p in players])
        prob += lpSum([x[p] for p in players]) == 11
        prob += lpSum([x[p] * costs[p] for p in players]) <= budget
        prob += lpSum([x[p] for p in players if roles[p] == 'Batter']) >= 4
        prob += lpSum([x[p] for p in players if roles[p] == 'Bowler']) >= 4
        prob += lpSum([x[p] for p in players if roles[p] == 'All-Rounder']) >= 1

        prob.solve(PULP_CBC_CMD(msg=0))
        selected = [p for p in players if x[p].value() == 1]
        
        xi = player_pool[player_pool['player_name'].isin(selected)].sort_values(by='impact_score', ascending=False)
        st.success(f"Purse Spent: ₹{xi['est_price_cr'].sum():.2f} Cr / ₹{budget:.1f} Cr | Aggregate Impact: {xi['impact_score'].sum():.1f}")
        st.dataframe(xi[['player_name', 'role', 'est_price_cr', 'impact_score', 'total_runs', 'total_wickets']], use_container_width=True)
