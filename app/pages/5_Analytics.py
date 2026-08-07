import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from queries import (
    get_team_epa_offense_defense,
    get_available_seasons,
    get_team_logos,
    style_dataframe,
    render_table,
    get_passing_leaderboard_season,
    get_rushing_leaderboard_season,
    get_receiving_leaderboard_season,
)

from styles import PAGE_FONT_CSS


# ==========================================================
# CONFIGURATION PAGE
# ==========================================================

st.set_page_config(
    page_title="Analytics",
    layout="wide"
)

st.markdown(
    PAGE_FONT_CSS,
    unsafe_allow_html=True
)


# ==========================================================
# CONSTANTES
# ==========================================================

AXE_MIN = -0.20
AXE_MAX = 0.20

LOGO_SIZE = 0.022

FIGURE_HEIGHT = 700



# ==========================================================
# GRAPHIQUE EQUIPE : HELPERS
# ==========================================================


def add_quadrant_background(fig):

    """
    Ajoute un découpage visuel du graphique :
    - Elite
    - Défense forte
    - Attaque forte
    - Reconstruction
    """

    zones = [
        (0, AXE_MAX, AXE_MIN, 0),
        (AXE_MIN, 0, AXE_MIN, 0),
        (0, AXE_MAX, 0, AXE_MAX),
        (AXE_MIN, 0, 0, AXE_MAX),
    ]

    for x0, x1, y0, y1 in zones:

        fig.add_shape(
            type="rect",
            x0=x0,
            x1=x1,
            y0=y0,
            y1=y1,
            line_width=0,
            layer="below",
        )



def add_net_epa_lines(fig):

    """
    Ajoute les diagonales de Net EPA.

    Net EPA = EPA attaque - EPA défense

    Elles sont fixes pour permettre
    la comparaison entre saisons.
    """

    levels = [
        -0.15,
        -0.10,
        -0.05,
        0,
        0.05,
        0.10,
        0.15,
    ]


    for level in levels:

        fig.add_shape(
            type="line",
            x0=AXE_MIN,
            y0=AXE_MIN - level,
            x1=AXE_MAX,
            y1=AXE_MAX - level,
            line=dict(
                color="lightgray",
                width=1,
                dash="dot",
            ),
            layer="below",
        )


        fig.add_annotation(
            x=0.18,
            y=0.18-level,
            text=f"Net {level:+.2f}",
            showarrow=False,
            font=dict(
                size=10
            ),
        )



def add_quadrant_labels(fig):

    labels = [
        (
            0.13,
            -0.13,
            "Elite<br>Attaque + Défense"
        ),
        (
            -0.13,
            -0.13,
            "Défense dominante"
        ),
        (
            0.13,
            0.13,
            "Attaque dominante"
        ),
        (
            -0.13,
            0.13,
            "Reconstruction"
        ),
    ]


    for x, y, text in labels:

        fig.add_annotation(
            x=x,
            y=y,
            text=f"<b>{text}</b>",
            showarrow=False,
            font=dict(
                size=13
            ),
        )



def add_team_hover(fig, df):

    """
    Trace invisible uniquement utilisé
    pour le hover.
    """

    fig.add_trace(
        go.Scatter(
            x=df["epa_offense"],
            y=df["epa_defense"],
            mode="markers",

            marker=dict(
                size=50,
                opacity=0,
            ),

            customdata=df[
                [
                    "team_name",
                    "plays_offense",
                    "plays_defense",
                ]
            ],

            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "<br>"
                "EPA attaque : %{x:.3f}<br>"
                "EPA défense : %{y:.3f}<br>"
                "<br>"
                "Actions offensives : %{customdata[1]}<br>"
                "Actions défensives : %{customdata[2]}"
                "<extra></extra>"
            ),

            showlegend=False,
        )
    )



def add_team_logos(fig, df):

    for _, row in df.iterrows():

        logo = row["logo_url"]

        if isinstance(logo, str) and logo:

            fig.add_layout_image(
                dict(
                    source=logo,

                    xref="x",
                    yref="y",

                    x=row["epa_offense"],
                    y=row["epa_defense"],

                    sizex=LOGO_SIZE,
                    sizey=LOGO_SIZE,

                    xanchor="center",
                    yanchor="middle",

                    layer="above",
                )
            )



def configure_team_axes(fig):

    fig.update_xaxes(
        range=[
            AXE_MIN,
            AXE_MAX
        ],
        zeroline=True,
    )


    fig.update_yaxes(
        range=[
            AXE_MAX,
            AXE_MIN
        ],
        zeroline=True,
    )


    fig.update_layout(

        height=FIGURE_HEIGHT,

        xaxis_title=(
            "EPA offensif par action "
            "(droite = meilleure attaque)"
        ),

        yaxis_title=(
            "EPA défensif par action "
            "(haut = meilleure défense)"
        ),

        margin=dict(
            l=40,
            r=40,
            t=50,
            b=40,
        )
    )



def build_team_chart(df):

    fig = go.Figure()

    add_quadrant_background(fig)

    add_net_epa_lines(fig)

    add_quadrant_labels(fig)

    add_team_hover(fig, df)

    add_team_logos(fig, df)

    configure_team_axes(fig)

    return fig


# ==========================================================
# TABLEAUX JOUEURS : HELPERS
# ==========================================================


def config_entier(label):

    return st.column_config.NumberColumn(
        label,
        format="%d"
    )



def config_decimal(label):

    return st.column_config.NumberColumn(
        label,
        format="%.1f"
    )



def afficher_leaderboard(
    df,
    colonnes_entieres,
    colonnes_decimales
):

    """
    Affichage générique des classements joueurs.

    Utilise st.dataframe natif :
    - tri par colonne
    - largeur automatique
    - affichage image
    """

    if df.empty:

        st.info(
            "Aucune donnée disponible avec ces filtres."
        )

        return


    configuration = {

        "photo_url":
            st.column_config.ImageColumn(
                "Photo",
                width="small"
            ),


        "Player":
            st.column_config.TextColumn(
                "Joueur",
                width="medium"
            ),


        "team":
            st.column_config.TextColumn(
                "Équipe",
                width="small"
            ),

    }


    for colonne in colonnes_entieres:

        if colonne in df.columns:

            configuration[colonne] = config_entier(
                colonne
            )



    for colonne in colonnes_decimales:

        if colonne in df.columns:

            configuration[colonne] = config_decimal(
                colonne
            )



    ordre_colonnes = [
        "photo_url",
        "Player",
        "team",
    ]


    ordre_colonnes += [
        colonne
        for colonne in df.columns
        if colonne not in ordre_colonnes
        and colonne != "player_id"
    ]



    st.dataframe(

        df,

        column_config=configuration,

        column_order=ordre_colonnes,

        hide_index=True,

        use_container_width=True,

        height=650,

    )



# ==========================================================
# FILTRES JOUEURS
# ==========================================================


def filtre_passe():

    return st.number_input(
        "Tentatives de passe minimum",
        min_value=0,
        value=100,
        step=25,
    )



def filtre_course():

    return st.number_input(
        "Tentatives de course minimum",
        min_value=0,
        value=50,
        step=10,
    )



def filtre_reception():

    return st.number_input(
        "Cibles minimum",
        min_value=0,
        value=40,
        step=10,
    )



# ==========================================================
# CHARGEMENT DATA JOUEURS
# ==========================================================


def afficher_passeurs(season):

    st.subheader(
        "Passeurs — saison complète"
    )


    minimum = filtre_passe()


    df = get_passing_leaderboard_season(
        season
    )


    df = df[
        df["Att"] >= minimum
    ]


    afficher_leaderboard(

        df,

        colonnes_entieres=[
            "Pass Yds",
            "Att",
            "Cmp",
            "TD",
            "INT",
            "1st",
            "20+",
            "40+",
            "Lng",
            "Sck",
            "SckY",
        ],

        colonnes_decimales=[
            "Yds/Att",
            "Cmp%",
            "Rate",
            "1st%",
        ]

    )



def afficher_coureurs(season):

    st.subheader(
        "Coureurs — saison complète"
    )


    minimum = filtre_course()


    df = get_rushing_leaderboard_season(
        season
    )


    df = df[
        df["Att"] >= minimum
    ]


    afficher_leaderboard(

        df,

        colonnes_entieres=[
            "Rush Yds",
            "Att",
            "TD",
            "20+",
            "40+",
            "Lng",
            "Rush 1st",
            "Rush FUM",
        ],

        colonnes_decimales=[
            "Rush 1st%",
        ]

    )



def afficher_receveurs(season):

    st.subheader(
        "Receveurs — saison complète"
    )


    minimum = filtre_reception()


    df = get_receiving_leaderboard_season(
        season
    )


    df = df[
        df["Tgts"] >= minimum
    ]


    afficher_leaderboard(

        df,

        colonnes_entieres=[
            "Rec",
            "Yds",
            "TD",
            "20+",
            "40+",
            "LNG",
            "Rec 1st",
            "Rec FUM",
            "Tgts",
        ],

        colonnes_decimales=[
            "1st%",
            "Rec YAC/R",
        ]

    )


# ==========================================================
# PAGE ANALYTICS
# ==========================================================


st.title(
    "Analytics"
)


# ==========================================================
# SELECTEUR SAISON
# ==========================================================


seasons = get_available_seasons()


season = st.selectbox(

    "Saison",

    seasons,

    index=len(seasons) - 1

)



# ==========================================================
# TABS PRINCIPAUX
# ==========================================================


tab_team, tab_players = st.tabs(
    [
        "Équipe",
        "Joueurs",
    ]
)



# ==========================================================
# ONGLET EQUIPE
# ==========================================================


with tab_team:


    st.subheader(
        "NFL Power Tiers"
    )


    st.caption(
        "Qui domine réellement la ligue : "
        "attaque, défense ou les deux."
    )


    df_team = get_team_epa_offense_defense(
        season
    )


    logos = get_team_logos()


    df_team["logo_url"] = (
        df_team["team"]
        .map(logos)
    )


    fig = build_team_chart(
        df_team
    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    st.subheader(
        "Détails équipes"
    )


    render_table(

        style_dataframe(

            df_team.drop(
                columns=[
                    "logo_url"
                ]
            )

        )

    )



# ==========================================================
# ONGLET JOUEURS
# ==========================================================


with tab_players:


    st.caption(
        "Classements saison complète "
        "avec filtres de volume minimum."
    )


    pass_tab, rush_tab, rec_tab = st.tabs(

        [
            "Passe",
            "Course",
            "Réception",
        ]

    )



    # --------------------------
    # PASSE
    # --------------------------

    with pass_tab:

        afficher_passeurs(
            season
        )



    # --------------------------
    # COURSE
    # --------------------------

    with rush_tab:

        afficher_coureurs(
            season
        )



    # --------------------------
    # RECEPTION
    # --------------------------

    with rec_tab:

        afficher_receveurs(
            season
        )



# ==========================================================
# OPTIMISATIONS STREAMLIT
# ==========================================================

# NOTE :
# Si tu veux activer le cache, déplace ces wrappers
# directement dans queries.py autour des fonctions SQL.
#
# Exemple :
#
# @st.cache_data(ttl=3600)
# def get_team_epa_offense_defense(season):
#     ...
#
# Cela évite de recharger les données à chaque interaction.


# ==========================================================
# SECURITE COLONNES JOUEURS
# ==========================================================


def ensure_player_columns(df):

    """
    Assure la présence des colonnes nécessaires
    pour l'affichage.

    Certaines sources nflfastR peuvent ne pas avoir
    photo_url ou team selon la saison.
    """

    if "photo_url" not in df.columns:

        df["photo_url"] = None


    if "team" not in df.columns:

        df["team"] = "-"


    if "Player" not in df.columns:

        if "player_name" in df.columns:

            df["Player"] = df["player_name"]

        else:

            df["Player"] = "-"


    return df



# ==========================================================
# VERSION SECURISEE DES LEADERBOARDS
# ==========================================================


# Sauvegarde des fonctions originales
# puis surcharge légère pour éviter les erreurs


_old_afficher_leaderboard = afficher_leaderboard



def afficher_leaderboard(

    df,

    colonnes_entieres,

    colonnes_decimales

):

    df = ensure_player_columns(
        df
    )


    _old_afficher_leaderboard(

        df,

        colonnes_entieres,

        colonnes_decimales

    )



# ==========================================================
# RESPONSIVE PLOTLY
# ==========================================================


def configure_responsive_chart(fig):

    fig.update_layout(

        autosize=True,

        dragmode=False,

        hovermode="closest",

    )

    return fig



# ==========================================================
# PATCH FINAL DU BUILD GRAPH
# ==========================================================


_old_build_team_chart = build_team_chart



def build_team_chart(df):

    fig = _old_build_team_chart(
        df
    )


    fig = configure_responsive_chart(
        fig
    )


    return fig