import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_team_epa_offense_defense, get_available_seasons, get_team_logos,
    style_dataframe, render_table,
    get_passing_leaderboard_season, get_rushing_leaderboard_season,
    get_receiving_leaderboard_season,
)
from styles import PAGE_FONT_CSS

st.set_page_config(page_title="Analytics", layout="wide")

st.markdown(PAGE_FONT_CSS, unsafe_allow_html=True)

st.title("Analytics")

seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

onglet_equipe, onglet_joueurs = st.tabs(["Équipe", "Joueurs"])

with onglet_equipe:
    st.subheader("NFL Power Tiers")
    st.caption("Qui domine vraiment la ligue — attaque, défense, ou les deux.")

    df = get_team_epa_offense_defense(season)
    logos = get_team_logos()
    df["logo_url"] = df["team"].map(logos)

    # Échelle fixe : plage réaliste de l'EPA/play au niveau équipe sur une
    # saison NFL, cohérente d'une saison à l'autre plutôt que recalculée à
    # partir des données (qui varierait légèrement selon la saison affichée).
    AXE_MIN, AXE_MAX = -0.2, 0.2

    taille_logo_x = 0.022
    taille_logo_y = 0.022

    x0_ligne = AXE_MIN
    x1_ligne = AXE_MAX

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
        marker=dict(size=44, opacity=0),
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

    fig.update_xaxes(range=[AXE_MIN, AXE_MAX])
    fig.update_yaxes(range=[AXE_MAX, AXE_MIN])  # inversé : EPA défensif négatif = bonne défense, donc en haut

    fig.update_layout(
        xaxis_title="EPA offensif par play (plus haut = meilleure attaque)",
        yaxis_title="EPA défensif par play (plus haut sur ce graphe = meilleure défense)",
        height=780,
    )

    st.plotly_chart(fig, use_container_width=True)

    render_table(style_dataframe(df.drop(columns=["logo_url"])))

def _config_entier(label):
    return st.column_config.NumberColumn(label, format="%d")

def _config_decimal(label):
    return st.column_config.NumberColumn(label, format="%.1f")

def _afficher_leaderboard(df, colonnes_entieres, colonnes_decimales):
    """Affiche un tableau de stats joueurs via st.dataframe (natif) plutôt
    que render_table/style_dataframe : tri au clic sur l'en-tête intégré
    d'origine, et les noms/colonnes ne débordent plus du tableau — deux
    limites propres au rendu HTML brut utilisé ailleurs dans l'app."""
    config = {
        "photo_url": st.column_config.ImageColumn(" ", width="small"),
        "Player": st.column_config.TextColumn("Player", width="medium"),
        "team": st.column_config.TextColumn("Équipe", width="small"),
    }
    for col in colonnes_entieres:
        config[col] = _config_entier(col)
    for col in colonnes_decimales:
        config[col] = _config_decimal(col)

    colonnes_visibles = ["photo_url", "Player", "team"] + [
        c for c in df.columns if c not in ("player_id", "photo_url", "Player", "team")
    ]
    st.dataframe(
        df, column_config=config, column_order=colonnes_visibles,
        hide_index=True, use_container_width=True, height=600,
    )

with onglet_joueurs:
    onglet_passe, onglet_course, onglet_reception = st.tabs(["Passe", "Course", "Réception"])

    with onglet_passe:
        st.subheader("Passeurs — saison complète")
        df_pass = get_passing_leaderboard_season(season)
        if df_pass.empty:
            st.info("Aucune donnée disponible pour cette saison.")
        else:
            _afficher_leaderboard(
                df_pass,
                colonnes_entieres=["Pass Yds", "Att", "Cmp", "TD", "INT", "1st", "20+", "40+", "Lng", "Sck", "SckY"],
                colonnes_decimales=["Yds/Att", "Cmp%", "Rate", "1st%"],
            )

    with onglet_course:
        st.subheader("Coureurs — saison complète")
        df_rush = get_rushing_leaderboard_season(season)
        if df_rush.empty:
            st.info("Aucune donnée disponible pour cette saison.")
        else:
            _afficher_leaderboard(
                df_rush,
                colonnes_entieres=["Rush Yds", "Att", "TD", "20+", "40+", "Lng", "Rush 1st", "Rush FUM"],
                colonnes_decimales=["Rush 1st%"],
            )

    with onglet_reception:
        st.subheader("Receveurs — saison complète")
        df_rec = get_receiving_leaderboard_season(season)
        if df_rec.empty:
            st.info("Aucune donnée disponible pour cette saison.")
        else:
            _afficher_leaderboard(
                df_rec,
                colonnes_entieres=["Rec", "Yds", "TD", "20+", "40+", "LNG", "Rec 1st", "Rec FUM", "Tgts"],
                colonnes_decimales=["1st%", "Rec YAC/R"],
            )