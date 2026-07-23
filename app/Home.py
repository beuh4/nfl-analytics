import streamlit as st

st.set_page_config(page_title="NFL Analytics", layout="wide", page_icon="🏈")

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