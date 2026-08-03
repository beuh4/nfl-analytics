import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from queries import (
    get_home_stats, get_home_current_season, get_home_recent_games, render_recent_games_list,
    get_top_qb_season_yards, get_top_rb_season_yards, get_top_wr_season_yards,
    get_top_qb_season_epa, get_team_epa_offense_defense,
    get_season_sacks_leader, get_season_interceptions_leader, get_season_success_rate_leader,
    render_insight_leaders,
)
from styles import HOME_CSS

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

stats = get_home_stats()

st.markdown(HOME_CSS, unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-eyebrow">Play-by-play · {stats['saison_min']}–{stats['saison_max']}</div>
    <h1 class="hero-title">NFL Analytics FR</h1>
    <p class="hero-tagline">Every team. Every player. Every play.</p>
</div>
<div class="stat-strip">
    <div class="stat-item"><div class="stat-value">{stats['total_plays']:,}</div><div class="stat-label">Plays</div></div>
    <div class="stat-item"><div class="stat-value">{stats['total_games']:,}</div><div class="stat-label">Games</div></div>
    <div class="stat-item"><div class="stat-value">{stats['total_teams']}</div><div class="stat-label">Teams</div></div>
    <div class="stat-item"><div class="stat-value">{stats['nb_saisons']}</div><div class="stat-label">Seasons</div></div>
</div>
""", unsafe_allow_html=True)


def display_navigation_card(icon: str, title: str, description: str, page_path: str) -> None:
    """Affiche une carte de navigation standardisée (icône + titre + description
    + lien). Utilisée 7 fois sur cette page — modifier le design ici suffit
    à le changer partout, plutôt que de retoucher chaque bloc individuellement."""
    with st.container(border=True):
        st.subheader(f"{icon} {title}")
        st.write(description)
        st.page_link(page_path, label="Ouvrir", icon="➡️")


# ─── Aperçu de la saison — insights, pas des tableaux ───
st.subheader("Aperçu de la saison")

home_season = get_home_current_season()
st.caption(f"Données de la saison {home_season}")


def _leader_entry(label, df, name_col, team_col, value_col, value_fmt, photo=True):
    """Construit une entrée pour render_insight_leaders à partir de la
    première ligne d'un DataFrame déjà trié — gère le cas où aucun joueur
    n'atteint encore le seuil qualifiant (ex. tout début de saison)."""
    if df.empty:
        return {"label": label, "name": "—", "team": None, "value": "—"}
    row = df.iloc[0]
    return {
        "label": label,
        "name": row[name_col],
        "team": row[team_col],
        "value": value_fmt(row[value_col]),
        "photo_url": row.get("photo_url") if photo else None,
    }


df_epa_ligue = get_team_epa_offense_defense(home_season)
df_off_epa_sorted = df_epa_ligue.sort_values("epa_offense", ascending=False)
df_def_epa_sorted = df_epa_ligue.sort_values("epa_defense", ascending=True)

league_leaders = [
    _leader_entry("Passing Yds", get_top_qb_season_yards(home_season), "player", "team", "yards", lambda v: f"{int(v):,}"),
    _leader_entry("Rushing Yds", get_top_rb_season_yards(home_season), "player", "team", "yards", lambda v: f"{int(v):,}"),
    _leader_entry("Receiving Yds", get_top_wr_season_yards(home_season), "player", "team", "yards", lambda v: f"{int(v):,}"),
    _leader_entry("Sacks", get_season_sacks_leader(home_season), "player", "team", "sacks", lambda v: f"{v:.1f}"),
    _leader_entry("Interceptions", get_season_interceptions_leader(home_season), "player", "team", "interceptions", lambda v: f"{int(v)}"),
]

analytics_leaders = [
    _leader_entry("EPA/Play", get_top_qb_season_epa(home_season), "player", "team", "epa_per_play", lambda v: f"{v:.3f}"),
    _leader_entry("Success Rate", get_season_success_rate_leader(home_season), "player", "team", "success_rate", lambda v: f"{v:.1%}"),
    {
        "label": "Offensive EPA",
        "name": df_off_epa_sorted.iloc[0]["team_name"] if not df_off_epa_sorted.empty else "—",
        "team": df_off_epa_sorted.iloc[0]["team"] if not df_off_epa_sorted.empty else None,
        "value": f"{df_off_epa_sorted.iloc[0]['epa_offense']:.3f}" if not df_off_epa_sorted.empty else "—",
    },
    {
        "label": "Defensive EPA",
        "name": df_def_epa_sorted.iloc[0]["team_name"] if not df_def_epa_sorted.empty else "—",
        "team": df_def_epa_sorted.iloc[0]["team"] if not df_def_epa_sorted.empty else None,
        "value": f"{df_def_epa_sorted.iloc[0]['epa_defense']:.3f}" if not df_def_epa_sorted.empty else "—",
    },
]

col_league, col_analytics, col_games = st.columns(3)

with col_league:
    st.write("**League Leaders**")
    render_insight_leaders(league_leaders)
    st.page_link("pages/4_Rankings.py", label="Voir tous les classements", icon="🏆")

with col_analytics:
    st.write("**Analytics Leaders** ⭐")
    render_insight_leaders(analytics_leaders)
    st.page_link("pages/5_Analytics.py", label="Explorer les analytics", icon="📊")

with col_games:
    st.write("**Derniers matchs**")
    render_recent_games_list(get_home_recent_games(home_season))
    st.page_link("pages/1_Teams.py", label="Explorer les équipes", icon="🏈")

st.divider()

# ─── Navigation principale ───
col1, col2, col3 = st.columns(3)
with col1:
    display_navigation_card(
        "🏈", "Teams",
        "Fiche complète par équipe : bilan, EPA, classement ligue, leaders, calendrier.",
        "pages/1_Teams.py",
    )
with col2:
    display_navigation_card(
        "👤", "Players",
        "Fiche joueur : bio, statistiques passing/rushing/receiving, EPA, pression, tendance.",
        "pages/2_Players.py",
    )
with col3:
    display_navigation_card(
        "🏟️", "Games",
        "Détail d'un match : score, drives, win probability, play-by-play.",
        "pages/3_Games.py",
    )

col4, col5, col6 = st.columns(3)
with col4:
    display_navigation_card(
        "🏆", "Rankings",
        "Meilleurs joueurs et équipes, semaine par semaine ou saison entière.",
        "pages/4_Rankings.py",
    )
with col5:
    display_navigation_card(
        "📊", "Analytics",
        "EPA offensif vs défensif, toutes les équipes de la ligue en un coup d'œil.",
        "pages/5_Analytics.py",
    )
with col6:
    display_navigation_card(
        "⚖️", "Compare",
        "Compare plusieurs équipes sur plusieurs années, offense ou défense.",
        "pages/6_Compare.py",
    )

display_navigation_card(
    "ℹ️", "About",
    "Source des données, méthodologie, et formulaire de retour.",
    "pages/7_About.py",
)

st.divider()

# ─── Feedback ───
with st.container(border=True):
    st.subheader("Un avis à partager ?")
    st.write("Ce projet est en phase de test. Tes retours m'aident à savoir quoi améliorer en priorité.")
    st.link_button("Donner mon avis", "https://docs.google.com/forms/d/e/TON_LIEN_ICI/viewform", icon="📝")