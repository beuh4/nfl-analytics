import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import get_team_epa_offense_defense, get_available_seasons, get_team_logos, style_dataframe, render_table

st.set_page_config(page_title="NFL Power Tiers", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.title("NFL Power Tiers")
st.caption("Qui domine vraiment la ligue — attaque, défense, ou les deux.")

seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

df = get_team_epa_offense_defense(season)
logos = get_team_logos()
df["logo_url"] = df["team"].map(logos)

x_min, x_max = df["epa_offense"].min(), df["epa_offense"].max()
y_min, y_max = df["epa_defense"].min(), df["epa_defense"].max()
x_range = x_max - x_min
y_range = y_max - y_min

taille_logo_x = max(x_range * 0.09, 0.01)
taille_logo_y = max(y_range * 0.09, 0.01)

# Marge visuelle pour que les diagonales couvrent tout le graphique,
# logos compris en bordure.
x0_ligne = x_min - x_range * 0.08
x1_ligne = x_max + x_range * 0.08

fig = go.Figure()

# ─── Diagonales de Net EPA (offense - défense concédée = constante) ───
# Chaque équipe sur la même diagonale a la même force globale nette.
net_epa = df["epa_offense"] - df["epa_defense"]
niveaux = 5
net_min, net_max = net_epa.min(), net_epa.max()
pas = (net_max - net_min) / (niveaux - 1) if niveaux > 1 else 0

for i in range(niveaux):
    niveau = net_min + i * pas
    fig.add_shape(
        type="line",
        x0=x0_ligne, y0=x0_ligne - niveau,
        x1=x1_ligne, y1=x1_ligne - niveau,
        line=dict(color="lightgray", width=1, dash="dot"),
        layer="below",
    )

# ─── Marqueurs invisibles : uniquement pour le hover ───
fig.add_trace(go.Scatter(
    x=df["epa_offense"],
    y=df["epa_defense"],
    mode="markers",
    marker=dict(size=32, opacity=0),
    customdata=df[["team_name", "plays_offense", "plays_defense"]],
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "EPA Offense : %{x:.3f}<br>"
        "EPA Défense : %{y:.3f}<br>"
        "Plays Off. : %{customdata[1]}<br>"
        "Plays Déf. : %{customdata[2]}"
        "<extra></extra>"
    ),
    showlegend=False,
))

for _, row in df.iterrows():
    if isinstance(row["logo_url"], str) and row["logo_url"]:
        fig.add_layout_image(
            dict(
                source=row["logo_url"],
                xref="x", yref="y",
                x=row["epa_offense"], y=row["epa_defense"],
                sizex=taille_logo_x, sizey=taille_logo_y,
                xanchor="center", yanchor="middle",
                layer="above",
            )
        )

fig.update_yaxes(autorange="reversed")  # EPA défensif négatif = bonne défense, donc en haut

fig.update_layout(
    xaxis_title="EPA offensif par play (plus haut = meilleure attaque)",
    yaxis_title="EPA défensif par play (plus haut sur ce graphe = meilleure défense)",
    height=700,
)

st.plotly_chart(fig, use_container_width=True)

render_table(style_dataframe(df.drop(columns=["logo_url"])))