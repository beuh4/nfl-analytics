import streamlit as st

st.set_page_config(page_title="About", layout="wide")
st.title("About")

st.write("""
NFL Analytics est un projet indépendant d'exploration des statistiques NFL,
construit avec Python, DuckDB et Streamlit.
""")

st.subheader("Source des données")
st.write("""
Toutes les données proviennent du projet [nflverse](https://github.com/nflverse),
via la librairie `nfl_data_py`, sous licence CC-BY. Les métriques EPA, CPOE et
de pression sont calculées par nflverse à partir du play-by-play officiel.
""")

st.divider()

with st.container(border=True):
    st.subheader("Un avis à partager ?")
    st.write("Ce projet est en phase de test. Tes retours m'aident à savoir quoi améliorer en priorité.")
    st.link_button("Donner mon avis", "https://docs.google.com/forms/d/e/1FAIpQLSdEDhXjqpZjaKdjrIXozICa3qRP9qvOj0pNRtt5L8GMemIPiw/viewform", icon="📝")