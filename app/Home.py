import streamlit as st

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}

.hero-banner {
    position: relative;
    overflow: hidden;
    background: linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    background-image:
        repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 1px, transparent 1px, transparent 64px),
        linear-gradient(180deg, #0F172A 0%, #111C33 100%);
    border-radius: 16px;
    padding: 56px 32px 44px;
    margin-bottom: 32px;
    text-align: center;
}
.hero-banner::after {
    content: "";
    position: absolute;
    left: 0; right: 0; bottom: 0;
    height: 14px;
    background-image: repeating-linear-gradient(90deg, rgba(234,88,12,0.55) 0px, rgba(234,88,12,0.55) 2px, transparent 2px, transparent 64px);
}
.hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    letter-spacing: 0.18em;
    color: #EA580C;
    text-transform: uppercase;
    margin-bottom: 12px;
    animation: hero-fade-in 0.6s ease-out;
}
.hero-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: clamp(2.2rem, 5vw, 3.4rem);
    color: #F8FAFC;
    margin: 0 0 10px;
    letter-spacing: -0.02em;
    animation: hero-fade-in 0.7s ease-out;
}
.hero-tagline {
    font-family: 'Manrope', sans-serif;
    font-size: 16px;
    color: #94A3B8;
    margin: 0;
    animation: hero-fade-in 0.8s ease-out;
}
@keyframes hero-fade-in {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
    .hero-eyebrow, .hero-title, .hero-tagline { animation: none; }
}
</style>

<div class="hero-banner">
    <div class="hero-eyebrow">Play-by-play · 2015–2026</div>
    <h1 class="hero-title">NFL Analytics</h1>
    <p class="hero-tagline">Explore les statistiques NFL saison par saison, semaine par semaine.</p>
</div>
""", unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("Synthèse hebdomadaire")
        st.write("Top performers, équipes qui sortent du lot, turnovers et pressions de la semaine.")
        st.page_link("pages/1_Synthese_Hebdomadaire.py", label="Ouvrir", icon="➡️")

with col2:
    with st.container(border=True):
        st.subheader("Synthèse annuelle")
        st.write("Meilleurs joueurs et équipes de la saison, en yards bruts et en EPA.")
        st.page_link("pages/2_Synthese_Annuelle.py", label="Ouvrir", icon="➡️")

with col3:
    with st.container(border=True):
        st.subheader("Attaque vs Défense")
        st.write("Positionnement de chaque équipe sur l'EPA offensif et défensif, saison par saison.")
        st.page_link("pages/3_Attaque_vs_Defense.py", label="Ouvrir", icon="➡️")

col4, col5 = st.columns(2)

with col4:
    with st.container(border=True):
        st.subheader("Évolution hebdomadaire")
        st.write("Suis la progression d'une équipe sur une saison précise, semaine après semaine.")
        st.page_link("pages/4_Evolution_Hebdomadaire.py", label="Ouvrir", icon="➡️")

with col5:
    with st.container(border=True):
        st.subheader("Évolution annuelle")
        st.write("Compare plusieurs équipes sur plusieurs années, sur l'axe offensif ou défensif.")
        st.page_link("pages/5_Evolution_Annuelle.py", label="Ouvrir", icon="➡️")

st.divider()

with st.container(border=True):
    st.subheader("Un avis à partager ?")
    st.write("Ce projet est en phase de test. Tes retours m'aident à savoir quoi améliorer en priorité.")
    st.link_button("Donner mon avis", "https://docs.google.com/forms/d/e/TON_LIEN_ICI/viewform", icon="📝")