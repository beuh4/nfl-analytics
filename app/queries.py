import duckdb
import streamlit as st
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


def get_top_qb_week(season: int, week: int, min_dropbacks: int = 10):
    con = get_connection()
    query = """
        SELECT passer_player_name AS player, posteam AS team,
               ROUND(AVG(epa), 3) AS epa_per_play, COUNT(*) AS dropbacks
        FROM plays
        WHERE season = ? AND week = ? AND qb_dropback = 1 AND passer_player_id IS NOT NULL
        GROUP BY passer_player_name, posteam
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
        SELECT rusher_player_name AS player, posteam AS team,
               ROUND(AVG(epa), 3) AS epa_per_play, COUNT(*) AS carries
        FROM plays
        WHERE season = ? AND week = ? AND rush = 1 AND rusher_player_id IS NOT NULL
        GROUP BY rusher_player_name, posteam
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
        SELECT receiver_player_name AS player, posteam AS team,
               ROUND(AVG(epa), 3) AS epa_per_play, COUNT(*) AS targets
        FROM plays
        WHERE season = ? AND week = ? AND pass = 1 AND receiver_player_id IS NOT NULL
        GROUP BY receiver_player_name, posteam
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


# Traduction des noms de colonnes techniques vers un affichage lisible en français.
# EPA reste tel quel (acronyme reconnu, pas de traduction naturelle utile).
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


def style_dataframe(df, team_col="team", decimals=3, couleur_unique=None):
    """Applique couleur de ligne (par équipe), contraste de texte, arrondi
    des décimales, traduction des colonnes, et style des en-têtes.

    couleur_unique : à utiliser quand le tableau ne concerne qu'une seule
    équipe (ex. page 2), donc pas de colonne "team" par ligne à mapper.
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