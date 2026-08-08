"""
Point d'entrée pour le déploiement Streamlit Cloud.

Ce fichier redirige vers la page d'accueil (app/Accueil.py).
"""

import streamlit as st
from pathlib import Path
import sys

# Ajouter le chemin vers app/ pour importer Accueil
sys.path.append(str(Path(__file__).resolve().parent / "app"))

# Rediriger vers Accueil.py
st.switch_page("app/Accueil.py")
