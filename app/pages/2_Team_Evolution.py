import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import get_all_teams, get_team_epa_by_week, get_seasons_for_team, get_team_colors, style_dataframe

st.set_page_config(page_title="Évolution EPA - Semaine par semaine", layout="wide")
st.title("Évolution EPA par équipe — semaine par semaine")

teams_df = get_all_teams()
team_name_to_abbr = dict(zip(teams_df["team_name"], teams_df["team_abbr"]))

col1, col2 = st.columns(2)
with col1:
    team_name = st.selectbox("Équipe", teams_df["team_name"])
    team_abbr = team_name_to_abbr[team_name]
with col2:
    seasons = get_seasons_for_team(team_abbr)
    season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

df = get_team_epa_by_week(team_abbr, season)

colors = get_team_colors()
couleur_equipe = colors.get(team_abbr, "#1f77b4")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["week"], y=df["epa_offense"], mode="lines+markers",
    name="EPA Offense", line=dict(color=couleur_equipe, width=3),
))
fig.add_trace(go.Scatter(
    x=df["week"], y=df["epa_defense"], mode="lines+markers",
    name="EPA Defense", line=dict(color=couleur_equipe, width=2, dash="dot"),
))
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(xaxis_title="Semaine", yaxis_title="EPA par play", height=600)
fig.update_xaxes(dtick=1)

st.plotly_chart(fig, use_container_width=True)
couleur_equipe = colors.get(team_abbr, "#1f77b4")
render_table(style_dataframe(df, couleur_unique=couleur_equipe))