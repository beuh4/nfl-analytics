import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import (
    get_all_teams, get_available_seasons, get_seasons_for_team, get_team_colors, get_team_logos,
    get_team_epa_offense_defense, get_team_epa_by_week, get_all_teams_records, get_team_schedule,
    get_team_qb_leaders, get_team_rb_leaders, get_team_wr_leaders, get_team_defensive_summary,
    style_dataframe, render_table, render_podium, couleur_texte_contraste,
)
import plotly.graph_objects as go

st.set_page_config(page_title="Teams", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
</style>
""", unsafe_allow_html=True)

teams_df = get_all_teams()
team_name_to_abbr = dict(zip(teams_df["team_name"], teams_df["team_abbr"]))
abbr_to_name = {v: k for k, v in team_name_to_abbr.items()}

# Identifiant équipe piloté par l'URL (?team=MIA) — équivalent fonctionnel
# d'une route dédiée, dans les limites de Streamlit Cloud.
team_abbr = st.query_params.get("team", teams_df["team_abbr"].iloc[0])
if team_abbr not in abbr_to_name:
    team_abbr = teams_df["team_abbr"].iloc[0]

col_select, col_season = st.columns([2, 1])
with col_select:
    team_name = st.selectbox("Équipe", teams_df["team_name"], index=list(team_name_to_abbr.keys()).index(abbr_to_name[team_abbr]))
    team_abbr = team_name_to_abbr[team_name]
    st.query_params["team"] = team_abbr

with col_season:
    seasons = get_seasons_for_team(team_abbr)
    season = st.selectbox("Saison", seasons, index=len(seasons) - 1)

colors = get_team_colors()
logos = get_team_logos()
couleur_equipe = colors.get(team_abbr, "#374151")
logo_url = logos.get(team_abbr, "")

# ─── En-tête équipe ───
records = get_all_teams_records(season)
record_row = records[records["team"] == team_abbr]
if not record_row.empty:
    wins = int(record_row["wins"].iloc[0])
    losses = int(record_row["losses"].iloc[0])
    ties = int(record_row["ties"].iloc[0])
else:
    wins = losses = ties = 0

team_info = teams_df[teams_df["team_abbr"] == team_abbr].iloc[0]

st.markdown(f"""
<div style="display:flex;align-items:center;gap:20px;padding:20px 0;">
    <img src="{logo_url}" height="80">
    <div>
        <div style="font-size:32px;font-weight:800;color:{couleur_equipe};">{team_info['team_name']}</div>
        <div style="font-size:16px;color:#64748B;">
            {wins}-{losses}{'-' + str(ties) if ties else ''} · Saison {season}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── EPA et classement ligue ───
df_epa_ligue = get_team_epa_offense_defense(season)
df_epa_ligue = df_epa_ligue.sort_values("epa_offense", ascending=False).reset_index(drop=True)
rang_offense = df_epa_ligue[df_epa_ligue["team"] == team_abbr].index[0] + 1 if team_abbr in df_epa_ligue["team"].values else None

df_epa_def_sorted = df_epa_ligue.sort_values("epa_defense", ascending=True).reset_index(drop=True)
rang_defense = df_epa_def_sorted[df_epa_def_sorted["team"] == team_abbr].index[0] + 1 if team_abbr in df_epa_def_sorted["team"].values else None

equipe_row = df_epa_ligue[df_epa_ligue["team"] == team_abbr]

col1, col2 = st.columns(2)
with col1:
    st.metric(
        "EPA Offense",
        f"{equipe_row['epa_offense'].iloc[0]:.3f}" if not equipe_row.empty else "—",
        f"#{rang_offense} / 32 en ligue" if rang_offense else None,
    )
with col2:
    st.metric(
        "EPA Défense (concédé)",
        f"{equipe_row['epa_defense'].iloc[0]:.3f}" if not equipe_row.empty else "—",
        f"#{rang_defense} / 32 en ligue" if rang_defense else None,
    )

st.divider()

# ─── Tendance EPA semaine par semaine (absorbé de l'ancienne page Team Evolution) ───
st.subheader("Tendance EPA — semaine par semaine")
df_weekly = get_team_epa_by_week(team_abbr, season)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_weekly["week"], y=df_weekly["epa_offense"], mode="lines+markers",
    name="EPA Offense", line=dict(color=couleur_equipe, width=3),
))
fig.add_trace(go.Scatter(
    x=df_weekly["week"], y=df_weekly["epa_defense"], mode="lines+markers",
    name="EPA Defense", line=dict(color=couleur_equipe, width=2, dash="dot"),
))
fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(xaxis_title="Semaine", yaxis_title="EPA par play", height=400)
fig.update_xaxes(dtick=1)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ─── Derniers et prochains matchs ───
schedule = get_team_schedule(team_abbr, season)
derniers = schedule[schedule["joue"]].tail(5).sort_values("week", ascending=False)
prochains = schedule[~schedule["joue"]].head(5)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Derniers matchs")
    if derniers.empty:
        st.info("Aucun match joué cette saison.")
    else:
        for _, row in derniers.iterrows():
            resultat = "V" if row["team_score"] > row["opp_score"] else ("D" if row["team_score"] < row["opp_score"] else "N")
            lieu = "vs" if row["domicile"] else "@"
            st.write(f"S{row['week']} — {resultat} {lieu} {row['opponent']} · {int(row['team_score'])}-{int(row['opp_score'])}")

with col2:
    st.subheader("Prochains matchs")
    if prochains.empty:
        st.info("Aucun match à venir programmé.")
    else:
        for _, row in prochains.iterrows():
            lieu = "vs" if row["domicile"] else "@"
            st.write(f"S{row['week']} — {lieu} {row['opponent']} · {row['gameday']}")

st.divider()

# ─── Leaders offensifs ───
st.subheader("Leaders offensifs")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Quarterback — EPA/dropback")
    render_podium(get_team_qb_leaders(team_abbr, season), metric_col="epa_per_play")
with col2:
    st.write("Running Back — EPA/course")
    render_podium(get_team_rb_leaders(team_abbr, season), metric_col="epa_per_play")
with col3:
    st.write("Receveur — EPA/cible")
    render_podium(get_team_wr_leaders(team_abbr, season), metric_col="epa_per_play")

st.divider()

# ─── Résumé défensif (niveau équipe, pas de détail joueur — voir limite schéma) ───
st.subheader("Résumé défensif")
def_summary = get_team_defensive_summary(team_abbr, season)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Interceptions", int(def_summary["interceptions"].iloc[0]))
col2.metric("Fumbles forcés", int(def_summary["fumbles_forces"].iloc[0]))
col3.metric("Sacks", f"{def_summary['sacks'].iloc[0]:.0f}")
col4.metric("Taux de pression", f"{def_summary['taux_pression'].iloc[0]:.1%}" if def_summary['taux_pression'].iloc[0] is not None else "—")