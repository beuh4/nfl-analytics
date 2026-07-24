import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_available_seasons, get_weeks_for_season, get_team_colors, couleur_texte_contraste,
    get_top_qb_week, get_top_rb_week, get_top_wr_week,
    get_best_offense_week, get_best_defense_week, get_biggest_surprises_week,
    get_explosive_plays_week, get_turnover_battle_week, get_pressure_leaders_week,
)

st.set_page_config(page_title="Synthèse hebdomadaire", layout="wide")
st.title("Synthèse hebdomadaire")


def style_by_team(df, team_col="team"):
    colors = get_team_colors()
    fonds = [colors.get(t, "#1f77b4") for t in df[team_col]]
    textes = [couleur_texte_contraste(c) for c in fonds]

    def colorer_ligne(row):
        i = df.index.get_loc(row.name)
        return [f"background-color: {fonds[i]}; color: {textes[i]}"] * len(row)

    return df.style.apply(colorer_ligne, axis=1)


seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

weeks = get_weeks_for_season(season)
week = st.selectbox("Semaine", weeks, index=len(weeks) - 1)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top 3 QB — EPA/dropback")
    df = get_top_qb_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)

with col2:
    st.subheader("Top 3 RB — EPA/course")
    df = get_top_rb_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)

with col3:
    st.subheader("Top 3 Receveurs — EPA/cible")
    df = get_top_wr_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Meilleure attaque de la semaine")
    df = get_best_offense_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)

with col2:
    st.subheader("Meilleure défense de la semaine")
    df = get_best_defense_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)

st.divider()

st.subheader("Équipes qui sortent du lot vs leur moyenne saison")
df = get_biggest_surprises_week(season, week)
col1, col2 = st.columns(2)
with col1:
    st.write("Plus forte surperformance")
    st.dataframe(style_by_team(df.head(3)), use_container_width=True, hide_index=True)
with col2:
    st.write("Plus forte contre-performance")
    st.dataframe(style_by_team(df.tail(3)), use_container_width=True, hide_index=True)

st.divider()

st.subheader("Plays explosifs")
top_teams, top_plays = get_explosive_plays_week(season, week)
col1, col2 = st.columns(2)
with col1:
    st.write("Équipes — nombre de plays explosifs")
    st.dataframe(style_by_team(top_teams), use_container_width=True, hide_index=True)
with col2:
    st.write("Top 5 plays de la semaine")
    st.dataframe(style_by_team(top_plays), use_container_width=True, hide_index=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Bataille des turnovers")
    df = get_turnover_battle_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)

with col2:
    st.subheader("Pressions générées")
    df = get_pressure_leaders_week(season, week)
    st.dataframe(style_by_team(df), use_container_width=True, hide_index=True)