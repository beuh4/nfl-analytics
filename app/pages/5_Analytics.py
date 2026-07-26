import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import get_team_epa_offense_defense, get_available_seasons, get_team_logos, style_dataframe, render_table

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
logos = get_team_logos()
df["logo_url"] = df["team"].map(logos)

# Taille des logos proportionnelle à l'étendue réelle des données, pas une
# valeur fixe — reste lisible quelle que soit la saison affichée.
x_range = df["epa_offense"].max() - df["epa_offense"].min()
y_range = df["epa_defense"].max() - df["epa_defense"].min()
taille_logo_x = max(x_range * 0.09, 0.01)
taille_logo_y = max(y_range * 0.09, 0.01)

fig = go.Figure()

# Marqueurs invisibles : uniquement pour le hover, les logos les remplacent visuellement.
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
fig.add_hline(y=df["epa_defense"].mean(), line_dash="dash", line_color="gray")
fig.add_vline(x=df["epa_offense"].mean(), line_dash="dash", line_color="gray")
fig.update_layout(
    xaxis_title="EPA offensif par play (plus haut = meilleure attaque)",
    yaxis_title="EPA défensif par play (plus haut sur ce graphe = meilleure défense)",
    height=700,
)

st.plotly_chart(fig, use_container_width=True)

render_table(style_dataframe(df.drop(columns=["logo_url"])))