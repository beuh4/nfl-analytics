# ─── En-tête équipe + EPA sur la même ligne ───
records = get_all_teams_records(season)
record_row = records[records["team"] == team_abbr]
if not record_row.empty:
    wins = int(record_row["wins"].iloc[0])
    losses = int(record_row["losses"].iloc[0])
    ties = int(record_row["ties"].iloc[0])
else:
    wins = losses = ties = 0

team_info = teams_df[teams_df["team_abbr"] == team_abbr].iloc[0]

df_epa_ligue = get_team_epa_offense_defense(season)
df_epa_ligue = df_epa_ligue.sort_values("epa_offense", ascending=False).reset_index(drop=True)
rang_offense = df_epa_ligue[df_epa_ligue["team"] == team_abbr].index[0] + 1 if team_abbr in df_epa_ligue["team"].values else None

df_epa_def_sorted = df_epa_ligue.sort_values("epa_defense", ascending=True).reset_index(drop=True)
rang_defense = df_epa_def_sorted[df_epa_def_sorted["team"] == team_abbr].index[0] + 1 if team_abbr in df_epa_def_sorted["team"].values else None

equipe_row = df_epa_ligue[df_epa_ligue["team"] == team_abbr]

col_logo, col_epa_off, col_epa_def = st.columns([2, 1, 1])

with col_logo:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:20px;padding:10px 0;">
        <img src="{logo_url}" height="80">
        <div>
            <div style="font-size:32px;font-weight:800;color:{couleur_equipe};">{team_info['team_name']}</div>
            <div style="font-size:16px;color:#64748B;">
                {wins}-{losses}{'-' + str(ties) if ties else ''} · Saison {season}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_epa_off:
    st.metric(
        "EPA Offense",
        f"{equipe_row['epa_offense'].iloc[0]:.3f}" if not equipe_row.empty else "—",
        f"#{rang_offense} / 32 en ligue" if rang_offense else None,
    )

with col_epa_def:
    st.metric(
        "EPA Défense (concédé)",
        f"{equipe_row['epa_defense'].iloc[0]:.3f}" if not equipe_row.empty else "—",
        f"#{rang_defense} / 32 en ligue" if rang_defense else None,
    )

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

# ─── Résumé défensif ───
st.subheader("Résumé défensif")
def_summary = get_team_defensive_summary(team_abbr, season)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Interceptions", int(def_summary["interceptions"].iloc[0]))
col2.metric("Fumbles forcés", int(def_summary["fumbles_forces"].iloc