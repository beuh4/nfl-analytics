import duckdb
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Chemin vers la base DuckDB, relatif à ce fichier pour fonctionner
# quel que soit le répertoire depuis lequel Streamlit est lancé.
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "nfl.duckdb"


def get_connection():
    # read_only=True évite un conflit de verrou si un job d'ingestion
    # écrit sur le fichier pendant qu'un utilisateur consulte l'app.
    return duckdb.connect(str(DB_PATH), read_only=True)


def get_available_seasons():
    con = get_connection()
    df = con.execute("SELECT DISTINCT season FROM plays ORDER BY season").fetchdf()
    con.close()
    return df["season"].tolist()


def get_team_epa_offense_defense(season: int):
    """EPA offensif et défensif par équipe pour une saison donnée."""
    con = get_connection()
    query = """
        WITH offense AS (
            SELECT posteam AS team, AVG(epa) AS epa_offense, COUNT(*) AS plays_offense
            FROM plays
            WHERE season = ? AND play_type IN ('pass', 'run') AND posteam IS NOT NULL
            GROUP BY posteam
        ),
        defense AS (
            SELECT defteam AS team, AVG(epa) AS epa_defense, COUNT(*) AS plays_defense
            FROM plays
            WHERE season = ? AND play_type IN ('pass', 'run') AND defteam IS NOT NULL
            GROUP BY defteam
        )
        SELECT
            o.team,
            t.team_name,
            t.team_color,
            o.epa_offense,
            d.epa_defense,
            o.plays_offense,
            d.plays_defense
        FROM offense o
        JOIN defense d ON o.team = d.team
        LEFT JOIN teams t ON o.team = t.team_abbr
        ORDER BY o.epa_offense DESC
    """
    df = con.execute(query, [season, season]).fetchdf()
    con.close()
    return df


def get_all_teams():
    con = get_connection()
    df = con.execute("SELECT team_abbr, team_name FROM teams ORDER BY team_name").fetchdf()
    con.close()
    return df


def get_team_epa_by_week(team: str, season: int):
    """EPA offensif/défensif semaine par semaine pour une équipe et une saison."""
    con = get_connection()
    query = """
        SELECT
            week,
            AVG(CASE WHEN posteam = ? THEN epa END) AS epa_offense,
            AVG(CASE WHEN defteam = ? THEN epa END) AS epa_defense
        FROM plays
        WHERE play_type IN ('pass', 'run')
          AND season = ?
          AND (posteam = ? OR defteam = ?)
        GROUP BY week
        ORDER BY week
    """
    df = con.execute(query, [team, team, season, team, team]).fetchdf()
    con.close()
    return df


def get_team_epa_by_season_multi(teams: list[str]):
    """EPA offensif/défensif saison par saison, pour plusieurs équipes en parallèle."""
    con = get_connection()
    placeholders = ", ".join(["?"] * len(teams))
    query = f"""
        WITH offense AS (
            SELECT season, posteam AS team, AVG(epa) AS epa_offense
            FROM plays
            WHERE play_type IN ('pass', 'run') AND posteam IN ({placeholders})
            GROUP BY season, posteam
        ),
        defense AS (
            SELECT season, defteam AS team, AVG(epa) AS epa_defense
            FROM plays
            WHERE play_type IN ('pass', 'run') AND defteam IN ({placeholders})
            GROUP BY season, defteam
        )
        SELECT o.season, o.team, o.epa_offense, d.epa_defense
        FROM offense o
        JOIN defense d ON o.season = d.season AND o.team = d.team
        ORDER BY o.season, o.team
    """
    df = con.execute(query, teams + teams).fetchdf()
    con.close()
    return df


def get_seasons_for_team(team: str):
    con = get_connection()
    query = """
        SELECT DISTINCT season FROM plays
        WHERE posteam = ? OR defteam = ?
        ORDER BY season
    """
    df = con.execute(query, [team, team]).fetchdf()
    con.close()
    return df["season"].tolist()


def get_team_colors():
    con = get_connection()
    df = con.execute("SELECT team_abbr, team_color FROM teams").fetchdf()
    con.close()
    return dict(zip(df["team_abbr"], df["team_color"]))


def get_team_logos():
    con = get_connection()
    df = con.execute("SELECT team_abbr, team_logo_espn FROM teams").fetchdf()
    con.close()
    return dict(zip(df["team_abbr"], df["team_logo_espn"]))


def couleur_texte_contraste(hex_color: str) -> str:
    """Calcule si un texte noir ou blanc est plus lisible sur un fond hexadécimal donné.
    Formule de luminance perçue ITU-R BT.601 : au-dessus de 0.6, le fond est
    jugé clair (texte noir), en dessous, sombre (texte blanc)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.6 else "#ffffff"


def get_weeks_for_season(season: int):
    con = get_connection()
    df = con.execute(
        "SELECT DISTINCT week FROM plays WHERE season = ? ORDER BY week", [season]
    ).fetchdf()
    con.close()
    return df["week"].tolist()


# ─────────────────────────────────────────────────────────────
# Requêtes hebdomadaires (Weekly Recap)
# ─────────────────────────────────────────────────────────────

def get_top_qb_week(season: int, week: int, min_dropbacks: int = 10):
    con = get_connection()
    query = """
        SELECT p.passer_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS dropbacks,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.passer_player_id = r.player_id
        WHERE p.season = ? AND p.week = ? AND p.qb_dropback = 1 AND p.passer_player_id IS NOT NULL
        GROUP BY p.passer_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, week, min_dropbacks]).fetchdf()
    con.close()
    return df


def get_top_rb_week(season: int, week: int, min_carries: int = 5):
    con = get_connection()
    query = """
        SELECT p.rusher_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS carries,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.rusher_player_id = r.player_id
        WHERE p.season = ? AND p.week = ? AND p.rush = 1 AND p.rusher_player_id IS NOT NULL
        GROUP BY p.rusher_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, week, min_carries]).fetchdf()
    con.close()
    return df


def get_top_wr_week(season: int, week: int, min_targets: int = 3):
    con = get_connection()
    query = """
        SELECT p.receiver_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS targets,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.receiver_player_id = r.player_id
        WHERE p.season = ? AND p.week = ? AND p.pass = 1 AND p.receiver_player_id IS NOT NULL
        GROUP BY p.receiver_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, week, min_targets]).fetchdf()
    con.close()
    return df


def get_best_offense_week(season: int, week: int):
    con = get_connection()
    query = """
        SELECT posteam AS team, ROUND(AVG(epa), 3) AS epa_offense, COUNT(*) AS plays
        FROM plays
        WHERE season = ? AND week = ? AND play_type IN ('pass', 'run') AND posteam IS NOT NULL
        GROUP BY posteam
        ORDER BY epa_offense DESC
        LIMIT 3
    """
    df = con.execute(query, [season, week]).fetchdf()
    con.close()
    return df


def get_best_defense_week(season: int, week: int):
    con = get_connection()
    query = """
        SELECT defteam AS team, ROUND(AVG(epa), 3) AS epa_allowed, COUNT(*) AS plays
        FROM plays
        WHERE season = ? AND week = ? AND play_type IN ('pass', 'run') AND defteam IS NOT NULL
        GROUP BY defteam
        ORDER BY epa_allowed ASC
        LIMIT 3
    """
    df = con.execute(query, [season, week]).fetchdf()
    con.close()
    return df


def get_biggest_surprises_week(season: int, week: int):
    """Compare l'EPA de la semaine à la moyenne du reste de la saison,
    pour repérer les équipes qui sortent nettement du lot (en bien ou en mal)."""
    con = get_connection()
    query = """
        WITH season_avg AS (
            SELECT posteam AS team, AVG(epa) AS avg_season
            FROM plays
            WHERE season = ? AND week != ? AND play_type IN ('pass', 'run') AND posteam IS NOT NULL
            GROUP BY posteam
        ),
        week_epa AS (
            SELECT posteam AS team, AVG(epa) AS avg_week
            FROM plays
            WHERE season = ? AND week = ? AND play_type IN ('pass', 'run') AND posteam IS NOT NULL
            GROUP BY posteam
        )
        SELECT w.team,
               ROUND(s.avg_season, 3) AS moyenne_saison,
               ROUND(w.avg_week, 3) AS cette_semaine,
               ROUND(w.avg_week - s.avg_season, 3) AS ecart
        FROM week_epa w
        JOIN season_avg s ON w.team = s.team
        ORDER BY ecart DESC
    """
    df = con.execute(query, [season, week, season, week]).fetchdf()
    con.close()
    return df


def get_explosive_plays_week(season: int, week: int):
    """Seuils : 20+ yards en passe, 10+ yards en course — standard NFL
    pour qualifier un jeu d'explosif."""
    con = get_connection()
    team_query = """
        SELECT posteam AS team, COUNT(*) AS explosive_plays
        FROM plays
        WHERE season = ? AND week = ?
          AND ((pass = 1 AND yards_gained >= 20) OR (rush = 1 AND yards_gained >= 10))
        GROUP BY posteam
        ORDER BY explosive_plays DESC
        LIMIT 5
    """
    top_teams = con.execute(team_query, [season, week]).fetchdf()

    plays_query = """
        SELECT COALESCE(passer_player_name, rusher_player_name) AS player,
               posteam AS team, play_type, yards_gained, ROUND(epa, 3) AS epa
        FROM plays
        WHERE season = ? AND week = ?
          AND ((pass = 1 AND yards_gained >= 20) OR (rush = 1 AND yards_gained >= 10))
        ORDER BY yards_gained DESC
        LIMIT 5
    """
    top_plays = con.execute(plays_query, [season, week]).fetchdf()
    con.close()
    return top_teams, top_plays


def get_turnover_battle_week(season: int, week: int):
    con = get_connection()
    query = """
        WITH giveaways AS (
            SELECT posteam AS team, COUNT(*) AS giveaways
            FROM plays
            WHERE season = ? AND week = ? AND (interception = 1 OR fumble_lost = 1)
            GROUP BY posteam
        ),
        takeaways AS (
            SELECT defteam AS team, COUNT(*) AS takeaways
            FROM plays
            WHERE season = ? AND week = ? AND (interception = 1 OR fumble_lost = 1)
            GROUP BY defteam
        )
        SELECT COALESCE(g.team, t.team) AS team,
               COALESCE(t.takeaways, 0) AS takeaways,
               COALESCE(g.giveaways, 0) AS giveaways,
               COALESCE(t.takeaways, 0) - COALESCE(g.giveaways, 0) AS differentiel
        FROM giveaways g
        FULL OUTER JOIN takeaways t ON g.team = t.team
        ORDER BY differentiel DESC
    """
    df = con.execute(query, [season, week, season, week]).fetchdf()
    con.close()
    return df


def get_pressure_leaders_week(season: int, week: int):
    con = get_connection()
    # CAST(... AS DOUBLE) plutôt que CASE WHEN was_pressure THEN :
    # la colonne peut être stockée en DOUBLE (0.0/1.0/NaN) après passage
    # par parquet, pas en booléen strict — DuckDB refuse sinon la comparaison.
    query = """
        SELECT defteam AS team,
               SUM(COALESCE(CAST(was_pressure AS DOUBLE), 0)) AS pressures,
               COUNT(*) AS pass_plays,
               ROUND(SUM(COALESCE(CAST(was_pressure AS DOUBLE), 0)) * 1.0 / COUNT(*), 3) AS taux_pression
        FROM plays
        WHERE season = ? AND week = ? AND pass = 1 AND defteam IS NOT NULL
        GROUP BY defteam
        ORDER BY pressures DESC
        LIMIT 5
    """
    df = con.execute(query, [season, week]).fetchdf()
    con.close()
    return df


# ─────────────────────────────────────────────────────────────
# Requêtes annuelles (Annual Recap) — stats brutes (yards)
# ─────────────────────────────────────────────────────────────

def get_top_qb_season_yards(season: int, min_dropbacks: int = 100):
    con = get_connection()
    query = """
        SELECT p.passer_player_name AS player, p.posteam AS team,
               SUM(p.passing_yards) AS yards, COUNT(*) AS dropbacks,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.passer_player_id = r.player_id
        WHERE p.season = ? AND p.qb_dropback = 1 AND p.passer_player_id IS NOT NULL
        GROUP BY p.passer_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season, min_dropbacks]).fetchdf()
    con.close()
    return df


def get_top_rb_season_yards(season: int, min_carries: int = 50):
    con = get_connection()
    query = """
        SELECT p.rusher_player_name AS player, p.posteam AS team,
               SUM(p.rushing_yards) AS yards, COUNT(*) AS carries,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.rusher_player_id = r.player_id
        WHERE p.season = ? AND p.rush = 1 AND p.rusher_player_id IS NOT NULL
        GROUP BY p.rusher_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season, min_carries]).fetchdf()
    con.close()
    return df


def get_top_wr_season_yards(season: int, min_targets: int = 30):
    con = get_connection()
    query = """
        SELECT p.receiver_player_name AS player, p.posteam AS team,
               SUM(p.receiving_yards) AS yards, COUNT(*) AS targets,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.receiver_player_id = r.player_id
        WHERE p.season = ? AND p.pass = 1 AND p.receiver_player_id IS NOT NULL
        GROUP BY p.receiver_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season, min_targets]).fetchdf()
    con.close()
    return df


def get_top_teams_offense_yards_season(season: int):
    con = get_connection()
    query = """
        SELECT posteam AS team, SUM(yards_gained) AS yards, COUNT(*) AS plays
        FROM plays
        WHERE season = ? AND play_type IN ('pass', 'run') AND posteam IS NOT NULL
        GROUP BY posteam
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season]).fetchdf()
    con.close()
    return df


# ─────────────────────────────────────────────────────────────
# Requêtes annuelles (Annual Recap) — EPA sur la saison entière
# ─────────────────────────────────────────────────────────────

def get_top_qb_season_epa(season: int, min_dropbacks: int = 100):
    con = get_connection()
    query = """
        SELECT p.passer_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS dropbacks,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.passer_player_id = r.player_id
        WHERE p.season = ? AND p.qb_dropback = 1 AND p.passer_player_id IS NOT NULL
        GROUP BY p.passer_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, min_dropbacks]).fetchdf()
    con.close()
    return df


def get_top_rb_season_epa(season: int, min_carries: int = 50):
    con = get_connection()
    query = """
        SELECT p.rusher_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS carries,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.rusher_player_id = r.player_id
        WHERE p.season = ? AND p.rush = 1 AND p.rusher_player_id IS NOT NULL
        GROUP BY p.rusher_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, min_carries]).fetchdf()
    con.close()
    return df


def get_top_wr_season_epa(season: int, min_targets: int = 30):
    con = get_connection()
    query = """
        SELECT p.receiver_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS targets,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.receiver_player_id = r.player_id
        WHERE p.season = ? AND p.pass = 1 AND p.receiver_player_id IS NOT NULL
        GROUP BY p.receiver_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, min_targets]).fetchdf()
    con.close()
    return df

def get_team_qb_leaders_yards(team: str, season: int, min_dropbacks: int = 20):
    con = get_connection()
    query = """
        SELECT p.passer_player_name AS player, p.posteam AS team,
               SUM(p.passing_yards) AS yards, COUNT(*) AS dropbacks,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.passer_player_id = r.player_id
        WHERE p.season = ? AND p.posteam = ? AND p.qb_dropback = 1 AND p.passer_player_id IS NOT NULL
        GROUP BY p.passer_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season, team, min_dropbacks]).fetchdf()
    con.close()
    return df


def get_team_rb_leaders_yards(team: str, season: int, min_carries: int = 10):
    con = get_connection()
    query = """
        SELECT p.rusher_player_name AS player, p.posteam AS team,
               SUM(p.rushing_yards) AS yards, COUNT(*) AS carries,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.rusher_player_id = r.player_id
        WHERE p.season = ? AND p.posteam = ? AND p.rush = 1 AND p.rusher_player_id IS NOT NULL
        GROUP BY p.rusher_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season, team, min_carries]).fetchdf()
    con.close()
    return df


def get_team_wr_leaders_yards(team: str, season: int, min_targets: int = 10):
    con = get_connection()
    query = """
        SELECT p.receiver_player_name AS player, p.posteam AS team,
               SUM(p.receiving_yards) AS yards, COUNT(*) AS targets,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.receiver_player_id = r.player_id
        WHERE p.season = ? AND p.posteam = ? AND p.pass = 1 AND p.receiver_player_id IS NOT NULL
        GROUP BY p.receiver_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY yards DESC
        LIMIT 3
    """
    df = con.execute(query, [season, team, min_targets]).fetchdf()
    con.close()
    return df

# ─────────────────────────────────────────────────────────────
# Traduction des colonnes et style des tableaux
# ─────────────────────────────────────────────────────────────

TRADUCTIONS_COLONNES = {
    "team": "Équipe",
    "team_name": "Nom",
    "epa_offense": "EPA Offense",
    "epa_defense": "EPA Défense",
    "epa_allowed": "EPA Concédé",
    "epa_per_play": "EPA/Play",
    "plays_offense": "Jeux Off.",
    "plays_defense": "Jeux Déf.",
    "week": "Semaine",
    "season": "Saison",
    "player": "Joueur",
    "dropbacks": "Dropbacks",
    "carries": "Courses",
    "targets": "Cibles",
    "plays": "Plays",
    "yards": "Yards",
    "moyenne_saison": "Moyenne Saison",
    "cette_semaine": "Cette Semaine",
    "ecart": "Écart",
    "explosive_plays": "Jeux Explosifs",
    "play_type": "Type de Jeu",
    "yards_gained": "Yards",
    "epa": "EPA",
    "takeaways": "Prises",
    "giveaways": "Pertes",
    "differentiel": "Différentiel",
    "pressures": "Pressions",
    "pass_plays": "Plays Passe",
    "taux_pression": "Taux Pression",
}


def style_dataframe(df, team_col="team", decimals=3, couleur_unique=None,
                     show_team_logos=True, player_col=None):
    """Applique couleur de ligne (par équipe), contraste de texte, arrondi
    des décimales, logo d'équipe, traduction des colonnes, et style des en-têtes.

    couleur_unique : à utiliser quand le tableau ne concerne qu'une seule
    équipe (ex. page 2), donc pas de colonne "team" par ligne à mapper.
    player_col : nom de la colonne joueur, si une colonne "photo_url" est
    présente dans df, pour combiner photo + nom dans la même cellule.
    """
    df = df.reset_index(drop=True).copy()

    if couleur_unique is not None:
        fonds = [couleur_unique] * len(df)
        affichage = df.copy()
    elif "team_color" in df.columns:
        fonds = df["team_color"].tolist()
        affichage = df.drop(columns=["team_color"])
    elif team_col in df.columns:
        colors = get_team_colors()
        fonds = [colors.get(t, "#1f77b4") for t in df[team_col]]
        affichage = df.copy()
    else:
        fonds = ["#f0f0f0"] * len(df)
        affichage = df.copy()

    textes = [couleur_texte_contraste(c) for c in fonds]

    def colorer_ligne(row):
        i = row.name
        return [f"background-color: {fonds[i]}; color: {textes[i]}"] * len(row)

    numeric_cols = affichage.select_dtypes(include="float").columns.tolist()

    if show_team_logos and team_col in affichage.columns:
        logos = get_team_logos()

        def _cell_avec_logo(abbr):
            url = logos.get(abbr)
            if url:
                return (
                    f'<span style="white-space:nowrap;">'
                    f'<img src="{url}" height="20" style="vertical-align:middle;margin-right:6px;">{abbr}'
                    f'</span>'
                )
            return abbr

        affichage[team_col] = affichage[team_col].apply(_cell_avec_logo)

    if player_col and player_col in affichage.columns and "photo_url" in affichage.columns:
        def _cell_avec_photo(row):
            url = row["photo_url"]
            nom = row[player_col]
            if isinstance(url, str) and url:
                return (
                    f'<span style="white-space:nowrap;">'
                    f'<img src="{url}" height="28" style="vertical-align:middle;margin-right:6px;border-radius:50%;">{nom}'
                    f'</span>'
                )
            return nom

        affichage[player_col] = affichage.apply(_cell_avec_photo, axis=1)
        affichage = affichage.drop(columns=["photo_url"])

    affichage = affichage.rename(columns=TRADUCTIONS_COLONNES)
    format_dict = {TRADUCTIONS_COLONNES.get(col, col): f"{{:.{decimals}f}}" for col in numeric_cols}

    header_styles = [
        {"selector": "th", "props": [
            ("background-color", "#111827"),
            ("color", "white"),
            ("font-weight", "600"),
            ("text-align", "left"),
            ("padding", "10px 14px"),
            ("border-bottom", "2px solid #374151"),
        ]},
        {"selector": "td", "props": [
            ("padding", "8px 14px"),
        ]},
        {"selector": "table", "props": [
            ("border-collapse", "collapse"),
            ("width", "100%"),
        ]},
    ]

    return (
        affichage.style
        .apply(colorer_ligne, axis=1)
        .format(format_dict)
        .set_table_styles(header_styles)
        .hide(axis="index")
    )


def render_table(styled_df):
    """Affiche un Styler pandas en HTML brut. Nécessaire car st.dataframe()
    ignore le style des en-têtes (set_table_styles) d'un Styler — il ne
    respecte que les couleurs cellule par cellule. Contrepartie : pas de
    tri interactif au clic sur une colonne."""
    html = styled_df.to_html()
    st.markdown(f'<div style="overflow-x:auto;">{html}</div>', unsafe_allow_html=True)


def render_podium(df, metric_col, decimals=3):
    """Podium HTML pour un top 3 de joueurs : 1er au centre (plus haut), 2e à
    gauche, 3e à droite. Utilise photo_url si présente dans df, sinon un avatar
    avec les initiales du joueur, coloré aux couleurs de l'équipe.

    Rendu via components.html (iframe isolé) pour éviter le scintillement
    du diffing React de st.markdown sur du HTML complexe. L'iframe n'hérite
    d'aucun style de la page parente : police et fond sont donc définis
    explicitement ci-dessous.
    """
    if df.empty:
        st.info("Aucune donnée disponible.")
        return

    colors = get_team_colors()
    logos = get_team_logos()

    couleurs_rang = ["#FBBF24", "#CBD5E1", "#D97706"]
    hauteurs = [130, 100, 80]
    ordre_affichage = [1, 0, 2] if len(df) >= 3 else list(range(len(df)))

    blocs = ""
    for i in ordre_affichage:
        if i >= len(df):
            continue
        row = df.iloc[i]
        rang = i + 1
        nom = row.get("player", "")
        team = row.get("team", "")
        valeur = row.get(metric_col, 0)
        couleur_equipe = colors.get(team, "#374151")
        logo_url = logos.get(team, "")
        photo_url = row.get("photo_url") if "photo_url" in df.columns else None

        if isinstance(photo_url, str) and photo_url:
            avatar = (
                f'<img src="{photo_url}" style="width:70px;height:70px;'
                f'border-radius:50%;object-fit:cover;border:3px solid {couleur_equipe};'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.3);">'
            )
        else:
            initiales = "".join([p[0] for p in nom.split(".") if p])[:2].upper() if nom else "?"
            avatar = (
                f'<div style="width:70px;height:70px;border-radius:50%;background:{couleur_equipe};'
                f'display:flex;align-items:center;justify-content:center;color:white;'
                f'font-weight:700;font-size:22px;border:3px solid {couleur_equipe};'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.3);">{initiales}</div>'
            )

        logo_html = (
            f'<img src="{logo_url}" height="18" style="vertical-align:middle;margin-right:4px;">'
            if logo_url else ""
        )

        blocs += f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;margin:0 10px;width:120px;">
            <div style="width:28px;height:28px;border-radius:50%;background:{couleurs_rang[rang-1]};
                        display:flex;align-items:center;justify-content:center;color:#1F2937;
                        font-weight:800;font-size:14px;margin-bottom:8px;">{rang}</div>
            {avatar}
            <div style="margin-top:8px;font-weight:600;text-align:center;font-size:14px;color:#1E293B;">{nom}</div>
            <div style="font-size:12px;color:#64748B;">{logo_html}{team}</div>
            <div style="margin-top:6px;font-weight:700;font-size:16px;color:#1E293B;">{valeur:,.{decimals}f}</div>
            <div style="width:100%;height:{hauteurs[rang-1]}px;
                        background:linear-gradient(180deg, {couleur_equipe}, {couleur_equipe}dd);
                        border-radius:8px 8px 0 0;margin-top:10px;"></div>
        </div>
        """

    html = f"""
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: 'Manrope', 'Segoe UI', sans-serif;
            }}
        </style>
    </head>
    <body>
        <div style="display:flex;align-items:flex-end;justify-content:center;padding:20px 0;">
            {blocs}
        </div>
    </body>
    </html>
    """
    components.html(html, height=320, scrolling=False)

def get_all_teams_records(season: int):
    """Bilan V/D/N de toutes les équipes pour une saison, calculé depuis
    la table games (un match compte pour les deux équipes via UNION ALL)."""
    con = get_connection()
    query = """
        WITH normalized AS (
            SELECT home_team AS team, home_score AS team_score, away_score AS opp_score
            FROM games WHERE season = ?
            UNION ALL
            SELECT away_team AS team, away_score AS team_score, home_score AS opp_score
            FROM games WHERE season = ?
        )
        SELECT team,
            SUM(CASE WHEN team_score > opp_score THEN 1 ELSE 0 END) AS wins,
            SUM(CASE WHEN team_score < opp_score THEN 1 ELSE 0 END) AS losses,
            SUM(CASE WHEN team_score = opp_score THEN 1 ELSE 0 END) AS ties
        FROM normalized
        WHERE team_score IS NOT NULL AND opp_score IS NOT NULL
        GROUP BY team
    """
    df = con.execute(query, [season, season]).fetchdf()
    con.close()
    total = df["wins"] + df["losses"] + df["ties"]
    df["win_pct"] = ((df["wins"] + 0.5 * df["ties"]) / total.replace(0, 1)).fillna(0)
    return df


def get_team_schedule(team: str, season: int):
    """Calendrier complet d'une équipe pour une saison, normalisé du point
    de vue de cette équipe (team_score/opp_score plutôt que home/away).
    Sert à la fois pour le bilan, les derniers matchs et les prochains matchs."""
    con = get_connection()
    query = """
        SELECT
            week, gameday,
            CASE WHEN home_team = ? THEN away_team ELSE home_team END AS opponent,
            CASE WHEN home_team = ? THEN TRUE ELSE FALSE END AS domicile,
            CASE WHEN home_team = ? THEN home_score ELSE away_score END AS team_score,
            CASE WHEN home_team = ? THEN away_score ELSE home_score END AS opp_score
        FROM games
        WHERE season = ? AND (home_team = ? OR away_team = ?)
        ORDER BY week
    """
    df = con.execute(query, [team, team, team, team, season, team, team]).fetchdf()
    con.close()
    df["joue"] = df["team_score"].notna() & df["opp_score"].notna()
    return df


def get_team_qb_leaders(team: str, season: int, min_dropbacks: int = 20):
    con = get_connection()
    query = """
        SELECT p.passer_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS dropbacks,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.passer_player_id = r.player_id
        WHERE p.season = ? AND p.posteam = ? AND p.qb_dropback = 1 AND p.passer_player_id IS NOT NULL
        GROUP BY p.passer_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, team, min_dropbacks]).fetchdf()
    con.close()
    return df


def get_team_rb_leaders(team: str, season: int, min_carries: int = 10):
    con = get_connection()
    query = """
        SELECT p.rusher_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS carries,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.rusher_player_id = r.player_id
        WHERE p.season = ? AND p.posteam = ? AND p.rush = 1 AND p.rusher_player_id IS NOT NULL
        GROUP BY p.rusher_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, team, min_carries]).fetchdf()
    con.close()
    return df


def get_team_wr_leaders(team: str, season: int, min_targets: int = 10):
    con = get_connection()
    query = """
        SELECT p.receiver_player_name AS player, p.posteam AS team,
               ROUND(AVG(p.epa), 3) AS epa_per_play, COUNT(*) AS targets,
               ANY_VALUE(r.headshot_url) AS photo_url
        FROM plays p
        LEFT JOIN rosters r ON p.receiver_player_id = r.player_id
        WHERE p.season = ? AND p.posteam = ? AND p.pass = 1 AND p.receiver_player_id IS NOT NULL
        GROUP BY p.receiver_player_name, p.posteam
        HAVING COUNT(*) >= ?
        ORDER BY epa_per_play DESC
        LIMIT 3
    """
    df = con.execute(query, [season, team, min_targets]).fetchdf()
    con.close()
    return df


def get_team_defensive_summary(team: str, season: int):
    """Résumé défensif au niveau équipe. Pas de détail par joueur :
    sack_player_id et les colonnes de tackle ne sont pas dans le schéma."""
    con = get_connection()
    query = """
        SELECT
            COUNT(*) FILTER (WHERE interception = 1) AS interceptions,
            COUNT(*) FILTER (WHERE fumble_lost = 1) AS fumbles_forces,
            SUM(CAST(sack AS DOUBLE)) AS sacks,
            ROUND(
                SUM(COALESCE(CAST(was_pressure AS DOUBLE), 0)) * 1.0
                / NULLIF(SUM(CASE WHEN pass = 1 THEN 1 ELSE 0 END), 0),
                3
            ) AS taux_pression
        FROM plays
        WHERE season = ? AND defteam = ?
    """
    df = con.execute(query, [season, team]).fetchdf()
    con.close()
    return df

def render_team_podium(df, metric_col, decimals=0):
    """Podium HTML pour un top 3 d'équipes (pas de joueur individuel) :
    logo d'équipe en grand format au centre de l'avatar, nom de l'équipe
    en dessous. Même structure visuelle que render_podium, adaptée aux
    entités équipe."""
    if df.empty:
        st.info("Aucune donnée disponible.")
        return

    colors = get_team_colors()
    logos = get_team_logos()

    couleurs_rang = ["#FBBF24", "#CBD5E1", "#D97706"]
    hauteurs = [130, 100, 80]
    ordre_affichage = [1, 0, 2] if len(df) >= 3 else list(range(len(df)))

    blocs = ""
    for i in ordre_affichage:
        if i >= len(df):
            continue
        row = df.iloc[i]
        rang = i + 1
        team = row.get("team", "")
        valeur = row.get(metric_col, 0)
        couleur_equipe = colors.get(team, "#374151")
        logo_url = logos.get(team, "")

        if logo_url:
            avatar = (
                f'<div style="width:70px;height:70px;border-radius:50%;background:white;'
                f'display:flex;align-items:center;justify-content:center;'
                f'border:3px solid {couleur_equipe};box-shadow:0 2px 8px rgba(0,0,0,0.3);">'
                f'<img src="{logo_url}" style="width:50px;height:50px;object-fit:contain;"></div>'
            )
        else:
            avatar = (
                f'<div style="width:70px;height:70px;border-radius:50%;background:{couleur_equipe};'
                f'display:flex;align-items:center;justify-content:center;color:white;'
                f'font-weight:700;font-size:18px;border:3px solid {couleur_equipe};'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.3);">{team}</div>'
            )

        blocs += f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;margin:0 10px;width:120px;">
            <div style="width:28px;height:28px;border-radius:50%;background:{couleurs_rang[rang-1]};
                        display:flex;align-items:center;justify-content:center;color:#1F2937;
                        font-weight:800;font-size:14px;margin-bottom:8px;">{rang}</div>
            {avatar}
            <div style="margin-top:8px;font-weight:600;text-align:center;font-size:14px;color:#1E293B;">{team}</div>
            <div style="margin-top:6px;font-weight:700;font-size:16px;color:#1E293B;">{valeur:,.{decimals}f}</div>
            <div style="width:100%;height:{hauteurs[rang-1]}px;
                        background:linear-gradient(180deg, {couleur_equipe}, {couleur_equipe}dd);
                        border-radius:8px 8px 0 0;margin-top:10px;"></div>
        </div>
        """

    html = f"""
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
            html, body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: 'Manrope', 'Segoe UI', sans-serif;
            }}
        </style>
    </head>
    <body>
        <div style="display:flex;align-items:flex-end;justify-content:center;padding:20px 0;">
            {blocs}
        </div>
    </body>
    </html>
    """
    components.html(html, height=320, scrolling=False)