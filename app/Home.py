import streamlit as st

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.title("NFL Analytics")
st.write("Explore les statistiques NFL saison par saison, semaine par semaine.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("Team Offense vs Defense")
        st.write("Positionnement de chaque équipe sur l'EPA offensif et défensif, saison par saison.")
        st.page_link("pages/1_Team_Offense.py", label="Ouvrir", icon="➡️")

with col2:
    with st.container(border=True):
        st.subheader("Évolution semaine par semaine")
        st.write("Suis la progression d'une équipe sur une saison précise, semaine après semaine.")
        st.page_link("pages/2_Team_Evolution.py", label="Ouvrir", icon="➡️")

with col3:
    with st.container(border=True):
        st.subheader("Évolution saison par saison")
        st.write("Compare plusieurs équipes sur plusieurs années, sur l'axe offensif ou défensif.")
        st.page_link("pages/3_Team_Evolution_Yearly.py", label="Ouvrir", icon="➡️")

col4, col5 = st.columns(2)

with col4:
    with st.container(border=True):
        st.subheader("Synthèse hebdomadaire")
        st.write("Top performers, équipes qui sortent du lot, turnovers et pressions de la semaine.")
        st.page_link("pages/4_Weekly_Recap.py", label="Ouvrir", icon="➡️")

with col5:
    with st.container(border=True):
        st.subheader("Synthèse annuelle")
        st.write("Meilleurs joueurs et équipes de la saison, en yards bruts et en EPA.")
        st.page_link("pages/5_Annual_Recap.py", label="Ouvrir", icon="➡️")

st.divider()

with st.container(border=True):
    st.subheader("Un avis à partager ?")
    st.write("Ce projet est en phase de test. Tes retours m'aident à savoir quoi améliorer en priorité.")
    st.link_button("Donner mon avis", "https://docs.google.com/forms/d/e/TON_LIEN_ICI/viewform", icon="📝")