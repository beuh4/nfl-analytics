import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_available_seasons, get_weeks_for_season, style_dataframe, render_table, render_podium, render_team_podium,
    get_top_qb_week, get_top_rb_week, get_top_wr_week,
    get_best_offense_week, get_best_defense_week, get_biggest_surprises_week,
    get_explosive_plays_week, get_turnover_battle_week, get_pressure_leaders_week,
    get_top_qb_season_yards, get_top_rb_season_yards, get_top_wr_season_yards,
    get_top_teams_offense_yards_season, get_top_qb_season_epa, get_top_rb_season_epa,
    get_team_weekly_movement, get_player_weekly_movement, render_ranking_with_movement,
    get_top_wr_season_epa, get_team_epa_offense_defense,
)
from styles import PAGE_FONT_CSS

st.set_page_config(page_title="Rankings", layout="wide")
st.markdown(PAGE_FONT_CSS, unsafe_allow_html=True)
st.title("Rankings")

# Sidebar avec filtre par saison global
seasons = get_available_seasons()
with st.sidebar:
    st.header("🔍 Filtres")
    selected_season = st.selectbox("Saison", seasons, index=len(seasons) - 1, key="rankings_season")

onglet_semaine, onglet_saison = st.tabs(["Cette semaine", "Cette saison"])

with onglet_semaine:
    weeks = get_weeks_for_season(selected_season)
    week = st.selectbox("Semaine", weeks, index=len(weeks) - 1, key="rank_week_week")

    # Podiums empilés en pleine largeur : render_podium utilise st.columns()
    # en interne pour son propre 1er/2e/3e — les imbriquer dans les st.columns
    # d'avant les rendait trop étroits pour afficher photo + nom correctement.
    st.divider()
    st.subheader("Top 3 QB — EPA/dropback")
    render_podium(get_top_qb_week(selected_season, week), metric_col="epa_per_play", season=selected_season, prefixe_cle="rank_sem_qb")
    st.subheader("Top 3 RB — EPA/course")
    render_podium(get_top_rb_week(selected_season, week), metric_col="epa_per_play", season=selected_season, prefixe_cle="rank_sem_rb")
    st.subheader("Top 3 Receveurs — EPA/cible")
    render_podium(get_top_wr_week(selected_season, week), metric_col="epa_per_play", season=selected_season, prefixe_cle="rank_sem_wr")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Meilleure attaque de la semaine")
        render_table(style_dataframe(get_best_offense_week(selected_season, week)))
    with col2:
        st.subheader("Meilleure défense de la semaine")
        render_table(style_dataframe(get_best_defense_week(selected_season, week)))

    st.divider()
    st.subheader("Équipes qui sortent du lot vs leur moyenne saison")
    df_surprises = get_biggest_surprises_week(selected_season, week)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Plus forte surperformance")
        render_table(style_dataframe(df_surprises.head(3)))
    with col2:
        st.write("Plus forte contre-performance")
        render_table(style_dataframe(df_surprises.tail(3)))

    st.divider()
    st.subheader("Plays explosifs")
    top_teams, top_plays = get_explosive_plays_week(selected_season, week)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Équipes — nombre de plays explosifs")
        render_table(style_dataframe(top_teams))
    with col2:
        st.write("Top 5 plays de la semaine")
        render_table(style_dataframe(top_plays))

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Bataille des turnovers")
        render_table(style_dataframe(get_turnover_battle_week(selected_season, week)))
    with col2:
        st.subheader("Pressions générées")
        if selected_season < 2023:
            st.caption("Donnée de pression partiellement disponible avant 2023.")
        render_table(style_dataframe(get_pressure_leaders_week(selected_season, week)))

    st.divider()
    st.subheader("Classement de la semaine — avec évolution")
    st.caption("▲ progression / ▼ recul vs semaine précédente · classé par EPA")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Équipes — EPA Offensif**")
        render_ranking_with_movement(get_team_weekly_movement(selected_season, week), value_col="epa_offense", prefixe_cle="rank_sem_mvt_team")
    with col2:
        st.write("**QB — EPA/Dropback**")
        render_ranking_with_movement(get_player_weekly_movement(selected_season, week, "passing"), value_col="epa_per_play", is_player=True, season=selected_season, prefixe_cle="rank_sem_mvt_qb")
    col3, col4 = st.columns(2)
    with col3:
        st.write("**RB — EPA/Course**")
        render_ranking_with_movement(get_player_weekly_movement(selected_season, week, "rushing"), value_col="epa_per_play", is_player=True, season=selected_season, prefixe_cle="rank_sem_mvt_rb")
    with col4:
        st.write("**Receveurs — EPA/Cible**")
        render_ranking_with_movement(get_player_weekly_movement(selected_season, week, "receiving"), value_col="epa_per_play", is_player=True, season=selected_season, prefixe_cle="rank_sem_mvt_wr")

with onglet_saison:
    season = selected_season
    st.caption("Pour la saison en cours, les statistiques reflètent uniquement les semaines déjà jouées.")

    st.divider()
    st.header("Statistiques brutes — Yards")
    st.subheader("Top 3 QB — Yards lancés")
    render_podium(get_top_qb_season_yards(selected_season), metric_col="yards", decimals=0, season=selected_season, prefixe_cle="rank_sai_qb_yds")
    st.subheader("Top 3 RB — Yards parcourus")
    render_podium(get_top_rb_season_yards(selected_season), metric_col="yards", decimals=0, season=selected_season, prefixe_cle="rank_sai_rb_yds")
    st.subheader("Top 3 Receveurs — Yards attrapés")
    render_podium(get_top_wr_season_yards(selected_season), metric_col="yards", decimals=0, season=selected_season, prefixe_cle="rank_sai_wr_yds")

    st.divider()
    st.subheader("Top 3 Équipes — Yards offensifs totaux")
    render_team_podium(get_top_teams_offense_yards_season(selected_season), metric_col="yards", decimals=0, prefixe_cle="rank_sai_team_yds")

    st.divider()
    st.header("Performance EPA")
    st.subheader("Top 3 QB — EPA/dropback")
    render_podium(get_top_qb_season_epa(selected_season), metric_col="epa_per_play", decimals=3, season=selected_season, prefixe_cle="rank_sai_qb_epa")
    st.subheader("Top 3 RB — EPA/course")
    render_podium(get_top_rb_season_epa(selected_season), metric_col="epa_per_play", decimals=3, season=selected_season, prefixe_cle="rank_sai_rb_epa")
    st.subheader("Top 3 Receveurs — EPA/cible")
    render_podium(get_top_wr_season_epa(selected_season), metric_col="epa_per_play", decimals=3, season=selected_season, prefixe_cle="rank_sai_wr_epa")

    st.divider()
    df_teams_epa = get_team_epa_offense_defense(selected_season)
    st.subheader("Top 3 Attaques — EPA offensif")
    render_team_podium(df_teams_epa.nlargest(3, "epa_offense").reset_index(drop=True), metric_col="epa_offense", decimals=3, prefixe_cle="rank_sai_atk_epa")
    st.subheader("Top 3 Défenses — EPA concédé le plus bas")
    render_team_podium(df_teams_epa.nsmallest(3, "epa_defense").reset_index(drop=True), metric_col="epa_defense", decimals=3, prefixe_cle="rank_sai_def_epa")
