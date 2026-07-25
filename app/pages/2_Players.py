import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_available_seasons, get_team_colors, get_team_logos,
    get_player_search_list, get_player_bio, get_player_passing_season,
    get_player_pressure_season, get_player_rushing_season, get_player_receiving_season,
    get_player_weekly_trend, get_player_games_played, convertir_taille_poids,
)

st.set_page_config(page_title="Players", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("Players")

seasons = get_available_seasons()
season = st.selectbox("Saison", seasons, index=len(seasons) - 1, key="player_season")

joueurs = get_player_search_list(season)

col_team, col_search = st.columns([1, 2])
with col_team:
    equipes_dispo = ["Toutes"] + sorted(joueurs["team"].dropna().unique().tolist())
    filtre_equipe = st.selectbox("Filtrer par équipe", equipes_dispo, key="player_team_filter")

joueurs_equipe = joueurs if filtre_equipe == "Toutes" else joueurs[joueurs["team"] == filtre_equipe]

with col_search:
    recherche = st.text_input("Rechercher un joueur", placeholder="Ex : Mahomes", key="player_search_box")

if recherche:
    joueurs_filtres = joueurs_equipe[joueurs_equipe["player_name"].str.contains(recherche, case=False, na=False)]
else:
    joueurs_filtres = joueurs_equipe

if joueurs_filtres.empty:
    st.warning("Aucun joueur trouvé pour ce filtre.")
    st.stop()

initial_id = st.query_params.get("player")
noms = joueurs_filtres["player_name"].tolist()
index_defaut = 0
if initial_id and initial_id in joueurs_filtres["player_id"].values:
    nom_initial = joueurs_filtres[joueurs_filtres["player_id"] == initial_id]["player_name"].iloc[0]
    if nom_initial in noms:
        index_defaut = noms.index(nom_initial)

nom_choisi = st.selectbox("Joueur", noms, index=index_defaut, key="player_select")
player_id = joueurs_filtres[joueurs_filtres["player_name"] == nom_choisi]["player_id"].iloc[0]
st.query_params["player"] = player_id

st.divider()

# ─── Bio ───
bio = get_player_bio(player_id, season)
if bio.empty:
    st.error("Aucune information disponible pour ce joueur.")
    st.stop()
bio = bio.iloc[0]

colors = get_team_colors()
logos = get_team_logos()
couleur_equipe = colors.get(bio["team"], "#374151")
logo_url = logos.get(bio["team"], "")
photo_url = bio["headshot_url"]

col_photo, col_info = st.columns([1, 3])
with col_photo:
    if isinstance(photo_url, str) and photo_url:
        st.markdown(
            f'<img src="{photo_url}" style="width:140px;height:140px;border-radius:50%;'
            f'object-fit:cover;border:4px solid {couleur_equipe};">',
            unsafe_allow_html=True,
        )
    else:
        initiales = "".join([p[0] for p in bio["player_name"].split(" ") if p])[:2].upper()
        st.markdown(
            f'<div style="width:140px;height:140px;border-radius:50%;background:{couleur_equipe};'
            f'display:flex;align-items:center;justify-content:center;color:white;'
            f'font-weight:700;font-size:44px;">{initiales}</div>',
            unsafe_allow_html=True,
        )

with col_info:
    st.markdown(f"""
    <div style="font-size:32px;font-weight:800;color:{couleur_equipe};">{bio['player_name']}</div>
    <div style="font-size:16px;color:#64748B;display:flex;align-items:center;gap:8px;margin-top:4px;">
        <img src="{logo_url}" height="24">{bio['team']} · {bio['position']}
    </div>
    """, unsafe_allow_html=True)

    metres, poids_kg = convertir_taille_poids(bio["height"], bio["weight"])
    age = int(bio["age"]) if bio["age"] == bio["age"] else "—"
    matchs = get_player_games_played(player_id, season)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Âge", age)
    col2.metric("Taille", f"{metres:.2f} m" if metres else "—")
    col3.metric("Poids", f"{poids_kg} kg" if poids_kg else "—")
    col4.metric("Matchs joués", matchs)

    # Texte simple, pas st.metric : évite la troncature sur les noms longs.
    universite = bio["college"] if isinstance(bio["college"], str) and bio["college"] else "—"
    experience = f"{int(bio['years_exp'])} ans" if bio["years_exp"] == bio["years_exp"] else "—"
    st.write(f"**Université :** {universite}  ·  **Expérience :** {experience}")

st.divider()

# ─── Passing ───
passing = get_player_passing_season(player_id, season)
if not passing.empty and passing["dropbacks"].iloc[0] and passing["dropbacks"].iloc[0] > 0:
    st.subheader("Passing")
    p = passing.iloc[0]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Tentatives", int(p["tentatives"]))
    col2.metric("Complétions", int(p["completions"]))
    col3.metric("Yards", f"{int(p['yards']):,}" if p["yards"] == p["yards"] else "—")
    col4.metric("TD / INT", f"{int(p['td'])} / {int(p['interceptions'])}")
    col5.metric("EPA/Dropback", f"{p['epa_per_play']:.3f}")

    col1, col2 = st.columns(2)
    col1.metric("CPOE", f"{p['cpoe']:+.1f}%" if p["cpoe"] == p["cpoe"] else "—")
    col2.metric("Air Yards Moy.", f"{p['air_yards_moy']:.1f}" if p["air_yards_moy"] == p["air_yards_moy"] else "—")

    pression = get_player_pressure_season(player_id, season)
    if not pression.empty:
        pr = pression.iloc[0]
        st.write("**Pression subie**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Dropbacks pressés", f"{pr['pressions_subies']:.0f}" if pr["pressions_subies"] == pr["pressions_subies"] else "—")
        col2.metric("Taux de pression", f"{pr['taux_pression']:.1%}" if pr["taux_pression"] == pr["taux_pression"] else "—")
        col3.metric("Sacks subis", f"{pr['sacks_subis']:.0f}" if pr["sacks_subis"] == pr["sacks_subis"] else "—")

    st.divider()

# ─── Rushing ───
rushing = get_player_rushing_season(player_id, season)
if not rushing.empty and rushing["courses"].iloc[0] and rushing["courses"].iloc[0] > 0:
    st.subheader("Rushing")
    r = rushing.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Courses", int(r["courses"]))
    col2.metric("Yards", f"{int(r['yards']):,}" if r["yards"] == r["yards"] else "—")
    col3.metric("TD", int(r["td"]))
    col4.metric("EPA/Course", f"{r['epa_per_play']:.3f}")
    st.divider()

# ─── Receiving ───
receiving = get_player_receiving_season(player_id, season)
if not receiving.empty and receiving["cibles"].iloc[0] and receiving["cibles"].iloc[0] > 0:
    st.subheader("Receiving")
    rc = receiving.iloc[0]
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Cibles", int(rc["cibles"]))
    col2.metric("Réceptions", int(rc["receptions"]))
    col3.metric("Yards", f"{int(rc['yards']):,}" if rc["yards"] == rc["yards"] else "—")
    col4.metric("TD", int(rc["td"]))
    col5.metric("EPA/Cible", f"{rc['epa_per_play']:.3f}")

    col1, col2 = st.columns(2)
    col1.metric("Air Yards Moy.", f"{rc['air_yards_moy']:.1f}" if rc["air_yards_moy"] == rc["air_yards_moy"] else "—")
    col2.metric("YAC Moy.", f"{rc['yac_moy']:.1f}" if rc["yac_moy"] == rc["yac_moy"] else "—")
    st.divider()

# ─── Tendance EPA — semaine par semaine ───
st.subheader("Tendance EPA — semaine par semaine")

roles_actifs = []
if not passing.empty and passing["dropbacks"].iloc[0] and passing["dropbacks"].iloc[0] > 0:
    roles_actifs.append(("passing", "Passing"))
if not rushing.empty and rushing["courses"].iloc[0] and rushing["courses"].iloc[0] > 0:
    roles_actifs.append(("rushing", "Rushing"))
if not receiving.empty and receiving["cibles"].iloc[0] and receiving["cibles"].iloc[0] > 0:
    roles_actifs.append(("receiving", "Receiving"))

if not roles_actifs:
    st.info("Aucune donnée hebdomadaire disponible.")
else:
    fig = go.Figure()
    styles = [dict(width=3), dict(width=2, dash="dot"), dict(width=2, dash="dash")]
    for (role, label), style in zip(roles_actifs, styles):
        df_trend = get_player_weekly_trend(player_id, season, role)
        fig.add_trace(go.Scatter(
            x=df_trend["week"], y=df_trend["epa_per_play"], mode="lines+markers",
            name=label, line=dict(color=couleur_equipe, **style),
        ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(xaxis_title="Semaine", yaxis_title="EPA par play", height=400)
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)