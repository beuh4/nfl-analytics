"""
Stub de compatibilité.

Le "Main file path" configuré sur Streamlit Cloud pointe encore vers
app/Home.py (ancien nom, avant renommage en app/Accueil.py). Ce fichier
existe uniquement pour rediriger vers la vraie page d'accueil et éviter
un FileNotFoundError au démarrage.

À supprimer une fois le Main file path mis à jour dans les réglages
Streamlit Cloud : app dashboard > Settings > General > Main file path
-> app/Accueil.py
"""
import streamlit as st

st.switch_page("Accueil.py")
