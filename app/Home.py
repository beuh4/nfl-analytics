import streamlit as st

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }

.hero-banner {
    position: relative; overflow: hidden;
    background: linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    background-image:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px, transparent 1px, transparent 64px),
        linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    border-radius: 16px; padding: 56px 32px 44px; margin-bottom: 32px; text-align: center;
}
.hero-banner::after {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 14px;
    background-image: repeating-linear-gradient(90deg, rgba(234,88,12,0.55) 0px, rgba(234,88,12,0.55) 2px, transparent 2px, transparent 64px);
}
.hero-eyebrow { font-family: 'Space Mono', monospace; font-size: 13px; letter-spacing: 0.18em; color: #EA580C; text-transform: uppercase; margin-bottom: 12px; }
.hero-title { font-weight: 800; font-size: clamp(2.2rem, 5vw, 3.4rem); color: #F8FAFC; margin: 0 0 10px; letter-spacing: -0.02em; }
.hero-tagline { font-size: 16px; color: #94A3B8; margin: 0; }
</style>

<div class="hero-banner">
    <div class="hero-eyebrow">Play-by-play · 2015–2026</div>
    <h1 class="hero-title">NFL Analytics</h1>
    <p class="hero-tagline">Explore les statistiques NFL saison par saison, semaine par semaine.</p>
</div>
""", unsafe_allow_html=True)

st.write("Utilise le menu à gauche pour naviguer : Teams, Players, Games, Rankings, Analytics, Compare, About.")