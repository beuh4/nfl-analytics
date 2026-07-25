import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import get_team_epa_offense_defense, get_available_seasons, style_dataframe, render_table

st.set_page_config(page_title="Analytics", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}
</style>
""", unsafe_allow_html=True)
st.title("EPA Offense vs EPA Defense par équipe")

seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

df = get_team_epa_offense_defense(season)

fig = px.scatter(
    df,
    x="epa_offense",
    y="epa_defense",
    text="team",
    hover_data=["team_name", "plays_offense", "plays_defense"],
)

fig.update_traces(
    textposition="top center",
    # Couleur de chaque point alignée sur la couleur réelle de l'équipe.
    marker=dict(size=14, color=df["team_color"], line=dict(width=1, color="black")),
)
fig.update_yaxes(autorange="reversed")  # EPA défensif négatif = bonne défense, donc en haut
fig.add_hline(y=df["epa_defense"].mean(), line_dash="dash", line_color="gray")
fig.add_vline(x=df["epa_offense"].mean(), line_dash="dash", line_color="gray")
fig.update_layout(
    xaxis_title="EPA offensif par play (plus haut = meilleure attaque)",
    yaxis_title="EPA défensif par play (plus haut sur ce graphe = meilleure défense)",
    height=700,
)

st.plotly_chart(fig, use_container_width=True)

render_table(style_dataframe(df))