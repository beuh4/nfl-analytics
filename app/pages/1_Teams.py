import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_all_teams, get_available_seasons, get_seasons_for_team, get_team_colors, get_team_logos,
    get_team_epa_offense_defense, get_team_epa_by_week, get_all_teams_records, get_team_schedule,
    get_team_qb_leaders, get_team_rb_leaders, get_team_wr_leaders, get_team_defensive_summary,
    style_dataframe, render_table, render_podium, couleur_texte_contraste,
)
import plotly.graph_objects as go

st.set_page_config(page_title="Teams", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
</style>
""", unsafe_allow_html=True)

teams_df = get_all_teams()
team_name_to_abbr = dict(zip(teams_df["team_name"], teams_df["team_abbr"]))
abbr_to_name = {v: k for k, v in team_name_to_abbr.items()}

# Identifiant équipe piloté par l'URL (?team=MIA) — équivalent fonctionnel
# d'une route dédiée, dans les limites de Streamlit Cloud.
team_abbr = st.query_params.get("team", teams_df["team_abbr"].iloc[0])
if team_abbr not in abbr_to_name:
    team_abbr = teams_df["team_abbr"].iloc[0]

col_select, col_season = st.columns([2, 1])
with col_select:
    team_name = st.selectbox("Équipe", teams_df["team_name"], index=list(team_name_to_abbr.keys()).index(abbr_to_name[team_abbr]))
    team_abbr = team_name_to_abbr[team_name]
    st.query_params["team"] = team_abbr

with col_season:
    seasons = get_seasons_for_team(team_abbr)
    season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

colors = get_team_colors()
logos = get_team_logos()
couleur_equipe = colors.get(team_abbr, "#374151")
logo_url = logos.get(team_abbr, "")

# ─── En-tête équipe + EPA sur la même ligne ───
records = get_all_teams_records(seas