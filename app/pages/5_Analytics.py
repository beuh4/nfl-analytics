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


st.set_page_config(
    page_title="Analytics",
    layout="wide"
)

st.markdown(
    PAGE_FONT_CSS,
    unsafe_allow_html=True
)


# ==========================
# CONFIG GRAPHIQUE
# ==========================

AXE_MIN = -0.20
AXE_MAX = 0.20

LOGO_SIZE = 0.022
FIGURE_HEIGHT = 700


# ==========================
# GRAPH TEAM
# ==========================


def _add_background(fig):

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


def _add_net_epa_lines(fig):

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
            y=0.18 - level,
            text=f"Net {level:+.2f}",
            showarrow=False,
            font=dict(size=10),
        )


def _add_quadrant_labels(fig):

    annotations = [
        (
            0.13,
            -0.13,
            "Elite<br>Attack + Defense"
        ),
        (
            -0.13,
            -0.13,
            "Defense First"
        ),
        (
            0.13,
            0.13,
            "Offense First"
        ),
        (
            -0.13,
            0.13,
            "Rebuild"
        ),
    ]

    for x, y, text in annotations:

        fig.add_annotation(
            x=x,
            y=y,
            text=f"<b>{text}</b>",
            showarrow=False,
            font=dict(size=13),
        )


def _add_hover(fig, df):

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
                    "plays_defense"
                ]
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "EPA Offense : %{x:.3f}<br>"
                "EPA Defense : %{y:.3f}<br>"
                "Offensive Plays : %{customdata[1]}<br>"
                "Defensive Plays : %{customdata[2]}"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )


def _add_team_logos(fig, df):

    for _, row in df.iterrows():

        if isinstance(row["logo_url"], str) and row["logo_url"]:

            fig.add_layout_image(
                dict(
                    source=row["logo_url"],
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


def _configure_axes(fig):

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
            "EPA offensif / play "
            "(droite = meilleure attaque)"
        ),
        yaxis_title=(
            "EPA défensif / play "
            "(haut = meilleure défense)"
        ),
        margin=dict(
            l=30,
            r=30,
            t=40,
            b=40,
        ),
    )


def build_team_chart(df):

    fig = go.Figure()

    _add_background(fig)

    _add_net_epa_lines(fig)

    _add_quadrant_labels(fig)

    _add_hover(fig, df)

    _add_team_logos(fig, df)

    _configure_axes(fig)

    return fig



# ==========================
# PLAYER TABLE
# ==========================


def _config_entier(label):

    return st.column_config.NumberColumn(
        label,
        format="%d"
    )


def _config_decimal(label):

    return st.column_config.NumberColumn(
        label,
        format="%.1f"
    )


def _afficher_leaderboard(
    df,
    colonnes_entieres,
    colonnes_decimales
):

    config = {

        "photo_url":
            st.column_config.ImageColumn(
                " ",
                width="small"
            ),

        "Player":
            st.column_config.TextColumn(
                "Player",
                width="medium"
            ),

        "team":
            st.column_config.TextColumn(
                "Équipe",
                width="small"
            ),
    }


    for col in colonnes_entieres:
        config[col] = _config_entier(col)


    for col in colonnes_decimales:
        config[col] = _config_decimal(col)


    ordre = [
        "photo_url",
        "Player",
        "team"
    ] + [
        c for c in df.columns
        if c not in [
            "player_id",
            "photo_url",
            "Player",
            "team"
        ]
    ]


    st.dataframe(
        df,
        column_config=config,
        column_order=ordre,
        hide_index=True,
        use_container_width=True,
        height=650,
    )



# ==========================
# PAGE
# ==========================


st.title("Analytics")


seasons = get_available_seasons()

season = st.selectbox(
    "Saison",
    seasons,
    index=len(seasons)-1
)


tab_team, tab_players = st.tabs(
    [
        "Équipe",
        "Joueurs"
    ]
)



# ==========================
# TEAM TAB
# ==========================


with tab_team:

    st.subheader(
        "NFL Power Tiers"
    )

    st.caption(
        "Qui domine réellement la ligue : attaque, défense ou les deux."
    )


    df = get_team_epa_offense_defense(
        season
    )


    logos = get_team_logos()

    df["logo_url"] = (
        df["team"]
        .map(logos)
    )


    fig = build_team_chart(df)


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    render_table(
        style_dataframe(
            df.drop(
                columns=[
                    "logo_url"
                ]
            )
        )
    )



# ==========================
# PLAYERS TAB
# ==========================


with tab_players:


    st.subheader(
        "Filtres"
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        min_pass = st.number_input(
            "Minimum Pass Attempts",
            min_value=0,
            value=100,
            step=25,
        )


    with c2:

        min_rush = st.number_input(
            "Minimum Rush Attempts",
            min_value=0,
            value=50,
            step=10,
        )


    with c3:

        min_targets = st.number_input(
            "Minimum Targets",
            min_value=0,
            value=40,
            step=10,
        )



    pass_tab, rush_tab, rec_tab = st.tabs(
        [
            "Passe",
            "Course",
            "Réception"
        ]
    )



    with pass_tab:

        df_pass = get_passing_leaderboard_season(
            season
        )

        df_pass = df_pass[
            df_pass["Att"] >= min_pass
        ]


        _afficher_leaderboard(
            df_pass,
            [
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
            [
                "Yds/Att",
                "Cmp%",
                "Rate",
                "1st%",
            ]
        )



    with rush_tab:

        df_rush = get_rushing_leaderboard_season(
            season
        )


        df_rush = df_rush[
            df_rush["Att"] >= min_rush
        ]


        _afficher_leaderboard(
            df_rush,
            [
                "Rush Yds",
                "Att",
                "TD",
                "20+",
                "40+",
                "Lng",
                "Rush 1st",
                "Rush FUM",
            ],
            [
                "Rush 1st%",
            ]
        )



    with rec_tab:

        df_rec = get_receiving_leaderboard_season(
            season
        )


        df_rec = df_rec[
            df_rec["Tgts"] >= min_targets
        ]


        _afficher_leaderboard(
            df_rec,
            [
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
            [
                "1st%",
                "Rec YAC/R",
            ]
        )