import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from queries import (
    get_home_stats, get_home_current_season, get_home_top_teams, get_home_top_players,
    get_home_recent_games, render_top_teams_list, render_top_players_list, render_recent_games_list,
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


# ─── Aperçu de la saison ───
st.subheader("Aperçu de la saison")

home_season = get_home_current_season()
st.caption(f"Données de la saison {home_season}")

col_teams, col_players, col_games = st.columns(3)

with col_teams:
    st.write("**Top 7 équipes — EPA Offensif**")
    render_top_teams_list(get_home_top_teams(home_season))
    st.page_link("pages/4_Rankings.py", label="Voir tous les classements", icon="🏆")

with col_players:
    st.write("**Top 5 joueurs offensifs — Yards**")
    poste_choisi = st.radio(
        "Poste", ["QB", "RB", "WR"], horizontal=True,
        key=f"home_poste_{home_season}", label_visibility="collapsed",
    )
    filtre_poste = None if poste_choisi == "Tous" else poste_choisi
    render_top_players_list(get_home_top_players(home_season, poste=filtre_poste))
    st.page_link("pages/2_Players.py", label="Explorer les joueurs", icon="👤")

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
