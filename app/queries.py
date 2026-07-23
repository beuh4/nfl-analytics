import duckdb
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "nfl.duckdb"


def get_connection():
    return duckdb.connect(str(DB_PATH), read_only=True)


def get_available_seasons():
    con = get_connection()
    df = con.execute("SELECT DISTINCT season FROM plays ORDER BY season").fetchdf()
    con.close()
    return df["season"].tolist()


def get_team_epa_offense_defense(season: int):
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
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.6 else "#ffffff"