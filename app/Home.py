import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from queries import get_home_stats

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

stats = get_home_stats()

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Manrope', sans-serif;
}}

.hero-banner {{
    position: relative;
    overflow: hidden;
    background:
        repeating-linear-gradient(
            90deg,
            rgba(255,255,255,0.05) 0px,
            rgba(255,255,255,0.05) 1px,
            transparent 1px,
            transparent 58px
        ),
        linear-gradient(180deg,#0F172A 0%,#111C33 100%);
    border-radius:16px 16px 0 0;
    padding:70px 40px 55px;
    text-align:center;
}}

.hero-eyebrow {{
    font-family:'Space Mono', monospace;
    font-size:13px;
    font-weight:700;
    letter-spacing:.20em;
    text-transform:uppercase;
    color:#F97316;
    margin-bottom:20px;
}}

.hero-title {{
    font-size:clamp(3rem,6vw,4.5rem);
    font-weight:800;
    color:#F8FAFC;
    letter-spacing:-0.04em;
    line-height:1;
    margin:0;
    text-shadow:
        0 2px 10px rgba(0,0,0,.35),
        0 0 24px rgba(255,255,255,.05);
}}

.hero-tagline {{
    margin-top:18px;
    font-size:1.25rem;
    color:#CBD5E1;
    font-weight:500;
}}

.stat-strip {{
    display:flex;
    justify-content:center;
    gap:60px;
    flex-wrap:wrap;

    background:#111C33;

    padding:28px 40px;

    border-radius:0 0 16px 16px;

    margin-bottom:35px;
}}

.stat-item {{
    text-align:center;
}}

.stat-value {{
    font-family:'Space Mono', monospace;
    font-size:30px;
    font-weight:700;
    color:#F97316;
}}

.stat-label {{
    margin-top:6px;
    font-size:12px;
    color:#94A3B8;
    letter-spacing:.12em;
    text-transform:uppercase;
}}

</style>

<div class="hero-banner">

    <div class="hero-eyebrow">
        Play-by-play • {stats['saison_min']}–{stats['saison_max']}
    </div>

    <div class="hero-title">
        NFL Analytics
    </div>

    <div class="hero-tagline">
        Every team. Every player. Every play.
    </div>

</div>

<div class="stat-strip">

    <div class="stat-item">
        <div class="stat-value">{stats['nb_saisons']}</div>
        <div class="stat-label">Seasons</div>
    </div>

    <div class="stat-item">
        <div class="stat-value">{stats['total_plays']:,}</div>
        <div class="stat-label">Plays</div>
    </div>

    <div class="stat-item">
        <div class="stat-value">{stats['total_teams']}</div>
        <div class="stat-label">Teams</div>
    </div>

    <div class="stat-item">
        <div class="stat-value">{stats['total_players']:,}</div>
        <div class="stat-label">Players</div>
    </div>

</div>
""", unsafe_allow_html=True)

st.divider()

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