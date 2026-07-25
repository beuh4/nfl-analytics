import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_available_seasons, render_podium, render_team_podium,
    get_top_qb_season_yards, get_top_rb_season_yards, get_top_wr_season_yards,
    get_top_teams_offense_yards_season,
    get_top_qb_season_epa, get_top_rb_season_epa, get_top_wr_season_epa,
    get_team_epa_offense_defense,
)

st.set_page_config(page_title="Synthèse annuelle", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.title("Synthèse annuelle")

seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

st.caption(
    "Pour la saison en cours, les statistiques reflètent uniquement les semaines déjà jouées."
)

st.divider()

# ─── Section 1 : statistiques brutes (yards) ───
st.header("Statistiques brutes — Yards")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top 3 QB — Yards lancés")
    df = get_top_qb_season_yards(season)
    render_podium(df, metric_col="yards", decimals=0)

with col2:
    st.subheader("Top 3 RB — Yards parcourus")
    df = get_top_rb_season_yards(season)
    render_podium(df, metric_col="yards", decimals=0)

with col3:
    st.subheader("Top 3 Receveurs — Yards attrapés")
    df = get_top_wr_season_yards(season)
    render_podium(df, metric_col="yards", decimals=0)

st.divider()

st.subheader("Top 3 Équipes — Yards offensifs totaux")
df_teams_yards = get_top_teams_offense_yards_season(season)
render_team_podium(df_teams_yards, metric_col="yards", decimals=0)

st.divider()

# ─── Section 2 : performance EPA ───
st.header("Performance EPA")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top 3 QB — EPA/dropback")
    df = get_top_qb_season_epa(season)
    render_podium(df, metric_col="epa_per_play", decimals=3)

with col2:
    st.subheader("Top 3 RB — EPA/course")
    df = get_top_rb_season_epa(season)
    render_podium(df, metric_col="epa_per_play", decimals=3)

with col3:
    st.subheader("Top 3 Receveurs — EPA/cible")
    df = get_top_wr_season_epa(season)
    render_podium(df, metric_col="epa_per_play", decimals=3)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 3 Attaques — EPA offensif")
    df_teams_epa = get_team_epa_offense_defense(season)
    top_off = df_teams_epa.nlargest(3, "epa_offense").reset_index(drop=True)
    render_team_podium(top_off, metric_col="epa_offense", decimals=3)

with col2:
    st.subheader("Top 3 Défenses — EPA concédé le plus bas")
    top_def = df_teams_epa.nsmallest(3, "epa_defense").reset_index(drop=True)
    render_team_podium(top_def, metric_col="epa_defense", decimals=3)