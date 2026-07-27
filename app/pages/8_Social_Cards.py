import streamlit as st
import sys
from io import BytesIO
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_available_seasons, get_all_teams, get_team_colors, get_team_logos,
    get_team_epa_offense_defense, get_player_search_list, get_player_bio,
    get_player_passing_season, get_player_rushing_season, get_player_receiving_season,
)
from social_cards import generer_carte_joueur, generer_carte_equipe

st.set_page_config(page_title="Social Cards", layout="wide")
st.title("Générateur de visuels — Instagram")
st.caption("Génère un visuel carré (1080×1080), prêt à télécharger et poster.")

type_carte = st.radio("Type de carte", ["Joueur", "Équipe"], horizontal=True)

seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

colors = get_team_colors()
logos = get_team_logos()

if type_carte == "Joueur":
    joueurs = get_player_search_list(season)
    nom_choisi = st.selectbox("Joueur", joueurs["player_name"].tolist())
    player_id = joueurs[joueurs["player_name"] == nom_choisi]["player_id"].iloc[0]

    bio = get_player_bio(player_id, season)
    if bio.empty:
        st.warning("Bio indisponible pour ce joueur.")
        st.stop()
    bio = bio.iloc[0]

    passing = get_player_passing_season(player_id, season)
    rushing = get_player_rushing_season(player_id, season)
    receiving = get_player_receiving_season(player_id, season)

    options_stat = {}
    if not passing.empty and passing["yards"].iloc[0] == passing["yards"].iloc[0]:
        options_stat[f"Passing Yards ({int(passing['yards'].iloc[0])})"] = ("YARDS PASSING", int(passing["yards"].iloc[0]))
        options_stat[f"EPA/Dropback ({passing['epa_per_play'].iloc[0]:.3f})"] = ("EPA/DROPBACK", f"{passing['epa_per_play'].iloc[0]:.3f}")
    if not rushing.empty and rushing["yards"].iloc[0] == rushing["yards"].iloc[0]:
        options_stat[f"Rushing Yards ({int(rushing['yards'].iloc[0])})"] = ("YARDS RUSHING", int(rushing["yards"].iloc[0]))
    if not receiving.empty and receiving["yards"].iloc[0] == receiving["yards"].iloc[0]:
        options_stat[f"Receiving Yards ({int(receiving['yards'].iloc[0])})"] = ("YARDS RECEIVING", int(receiving["yards"].iloc[0]))

    if not options_stat:
        st.warning("Aucune statistique disponible pour ce joueur sur cette saison.")
        st.stop()

    choix_stat = st.selectbox("Statistique à mettre en avant", list(options_stat.keys()))
    stat_label, stat_value = options_stat[choix_stat]

    if st.button("Générer le visuel"):
        img = generer_carte_joueur(
            nom=bio["player_name"], poste=bio["position"], team_abbr=bio["team"],
            team_color=colors.get(bio["team"], "#374151"), logo_url=logos.get(bio["team"], ""),
            photo_url=bio["headshot_url"], stat_label=stat_label, stat_value=stat_value,
        )
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        st.image(img, width=400)
        st.download_button("Télécharger le PNG", buffer.getvalue(),
                            file_name=f"{bio['player_name'].replace(' ', '_')}_{season}.png", mime="image/png")

else:
    teams_df = get_all_teams()
    team_name = st.selectbox("Équipe", teams_df["team_name"])
    team_abbr = teams_df[teams_df["team_name"] == team_name]["team_abbr"].iloc[0]

    df_epa = get_team_epa_offense_defense(season)
    df_off = df_epa.sort_values("epa_offense", ascending=False).reset_index(drop=True)
    df_def = df_epa.sort_values("epa_defense", ascending=True).reset_index(drop=True)

    if team_abbr not in df_epa["team"].values:
        st.warning("Données indisponibles pour cette équipe/saison.")
        st.stop()

    rang_off = df_off[df_off["team"] == team_abbr].index[0] + 1
    rang_def = df_def[df_def["team"] == team_abbr].index[0] + 1
    epa_off = df_epa[df_epa["team"] == team_abbr]["epa_offense"].iloc[0]
    epa_def = df_epa[df_epa["team"] == team_abbr]["epa_defense"].iloc[0]

    if st.button("Générer le visuel"):
        img = generer_carte_equipe(
            team_name=team_name, season=season, team_color=colors.get(team_abbr, "#374151"),
            logo_url=logos.get(team_abbr, ""), rang_off=rang_off, epa_off=epa_off,
            rang_def=rang_def, epa_def=epa_def,
        )
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        st.image(img, width=400)
        st.download_button("Télécharger le PNG", buffer.getvalue(),
                            file_name=f"{team_abbr}_{season}.png", mime="image/png")