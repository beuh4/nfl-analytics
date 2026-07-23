import streamlit as st
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from queries import get_all_teams, get_team_epa_by_season_multi, get_team_colors, couleur_texte_contraste

st.set_page_config(page_title="Évolution EPA - Saison par saison", layout="wide")
st.title("Évolution EPA par équipe — saison par saison")

teams_df = get_all_teams()
team_name_to_abbr = dict(zip(teams_df["team_name"], teams_df["team_abbr"]))

team_names = st.multiselect(
    "Équipes",
    teams_df["team_name"],
    default=[teams_df["team_name"].iloc[0]],
)

if team_names:
    colors = get_team_colors()
    badges_html = ""
    for name in team_names:
        abbr = team_name_to_abbr[name]
        couleur = colors.get(abbr, "#1f77b4")
        texte = couleur_texte_contraste(couleur)
        badges_html += (
            f'<span style="background-color:{couleur}; color:{texte}; '
            f'padding:4px 12px; border-radius:12px; margin-right:6px; '
            f'font-weight:600; display:inline-block;">{abbr}</span>'
        )
    st.markdown(badges_html, unsafe_allow_html=True)

if not team_names:
    st.info("Sélectionne au moins une équipe.")
    st.stop()

team_abbrs = [team_name_to_abbr[name] for name in team_names]

metric = st.radio("Métrique", ["epa_offense", "epa_defense"], horizontal=True)

df = get_team_epa_by_season_multi(team_abbrs)

colors = get_team_colors()

fig = go.Figure()
for team in team_abbrs:
    df_team = df[df["team"] == team]
    fig.add_trace(go.Scatter(
        x=df_team["season"], y=df_team[metric],
        mode="lines+markers", name=team,
        line=dict(color=colors.get(team, "#1f77b4"), width=3),
    ))


fig.add_hline(y=0, line_dash="dash", line_color="gray")
fig.update_layout(xaxis_title="Saison", yaxis_title="EPA par play", height=600)
fig.update_xaxes(dtick=1)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(df, use_container_width=True, hide_index=True)