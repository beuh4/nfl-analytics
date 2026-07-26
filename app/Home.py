import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from queries import (
    get_home_stats, get_home_current_season, get_home_top_teams, get_home_top_players,
    get_home_recent_games, render_top_teams_list, render_top_players_list, render_recent_games_list,
)

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

stats = get_home_stats()

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Manrope', sans-serif; }}

.hero-banner {{
    position: relative; overflow: hidden;
    background: linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    background-image:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px, transparent 1px, transparent 64px),
        linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    border-radius: 16px; padding: 18px 32px 0; margin-bottom: 0; text-align: center;
}}
.hero-eyebrow {{ font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.14em; color: #EA580C; text-transform: uppercase; margin-bottom: 4px; }}
.hero-title {{ font-weight: 800; font-size: clamp(1.3rem, 2.6vw, 1.8rem); color: #CBD5E1; margin: 0 0 3px; letter-spacing: -0.02em; }}
.hero-tagline {{ font-size: 13px; color: #94A3B8; margin: 0 0 12px; }}

.stat-strip {{
    display: flex; justify-content: center; gap: 36px;
    background: #111C33; padding: 10px 32px; border-radius: 0 0 16px 16px;
    margin-bottom: 24px; flex-wrap: wrap;
}}
.stat-item {{ text-align: center; }}
.stat-value {{ font-family: 'Space Mono', monospace; font-size: 17px; font-weight: 700; color: #EA580C; }}
.stat-label {{ font-size: 10px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 1px; }}
</style>

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

# ─── Aperçu de la saison ───
st.subheader("Aperçu de la saison")

home_season = get_home_current_season()
st.caption(f"Données de la saison {home_season}")

col_teams, col_players, col_games = st.columns(3)

with col_teams:
    st.write("**Top 5 équipes — EPA Offensif**")
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
    with st.container(border=True):
        st.subheader("🏈 Teams")
        st.write("Fiche complète par équipe : bilan, EPA, classement ligue, leaders, calendrier.")
        st.page_link("pages/1_Teams.py", label="Ouvrir", icon="➡️")
with col2:
    with st.container(border=True):
        st.subheader("👤 Players")
        st.write("Fiche joueur : bio, statistiques passing/rushing/receiving, EPA, pression, tendance.")
        st.page_link("pages/2_Players.py", label="Ouvrir", icon="➡️")
with col3:
    with st.container(border=True):
        st.subheader("🏟️ Games")
        st.write("Détail d'un match : score, drives, win probability, play-by-play.")
        st.page_link("pages/3_Games.py", label="Ouvrir", icon="➡️")

col4, col5, col6 = st.columns(3)
with col4:
    with st.container(border=True):
        st.subheader("🏆 Rankings")
        st.write("Meilleurs joueurs et équipes, semaine par semaine ou saison entière.")
        st.page_link("pages/4_Rankings.py", label="Ouvrir", icon="➡️")
with col5:
    with st.container(border=True):
        st.subheader("📊 Analytics")
        st.write("EPA offensif vs défensif, toutes les équipes de la ligue en un coup d'œil.")
        st.page_link("pages/5_Analytics.py", label="Ouvrir", icon="➡️")
with col6:
    with st.container(border=True):
        st.subheader("⚖️ Compare")
        st.write("Compare plusieurs équipes sur plusieurs années, offense ou défense.")
        st.page_link("pages/6_Compare.py", label="Ouvrir", icon="➡️")

with st.container(border=True):
    st.subheader("ℹ️ About")
    st.write("Source des données, méthodologie, et formulaire de retour.")
    st.page_link("pages/7_About.py", label="Ouvrir", icon="➡️")

st.divider()

# ─── Feedback ───
with st.container(border=True):
    st.subheader("Un avis à partager ?")
    st.write("Ce projet est en phase de test. Tes retours m'aident à savoir quoi améliorer en priorité.")
    st.link_button("Donner mon avis", "https://docs.google.com/forms/d/e/TON_LIEN_ICI/viewform", icon="📝")


