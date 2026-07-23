import nfl_data_py as nfl
from pathlib import Path

OUTPUT_DIR = Path("data/static")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLONNES_GAMES = [
    "game_id", "season", "week", "game_type", "gameday",
    "home_team", "away_team", "home_score", "away_score",
    "result", "total", "overtime",
    "roof", "surface", "temp", "wind",
    "stadium", "stadium_id",
    "home_coach", "away_coach",
    "div_game", "spread_line", "total_line",
]

COLONNES_PLAYERS = [

    "gsis_id", "display_name", "position", "team",
    "birth_date", "college_name", "draft_year", "draft_round", "draft_pick",
]

COLONNES_TEAMS = [
    "team_abbr", "team_name", "team_conf", "team_division",
    "team_color", "team_logo_espn",
]

SEASONS = list(range(2015, 2026))  # à ajuster selon l'historique retenu


def _select(df, colonnes, label):
    presentes = [c for c in colonnes if c in df.columns]
    absentes = [c for c in colonnes if c not in df.columns]
    if absentes:
        print(f"  Colonnes absentes pour {label} : {absentes}")
    return df[presentes]


def fetch_games():
    print("Téléchargement games...")
    df = nfl.import_schedules(SEASONS)
    df = _select(df, COLONNES_GAMES, "games")
    df.to_parquet(OUTPUT_DIR / "games.parquet", index=False)
    print(f"  Sauvegardé : games.parquet ({len(df)} lignes)")


def fetch_players():
    print("Téléchargement players...")
    df = nfl.import_players()
    df = _select(df, COLONNES_PLAYERS, "players")
    df.to_parquet(OUTPUT_DIR / "players.parquet", index=False)
    print(f"  Sauvegardé : players.parquet ({len(df)} lignes)")


def fetch_teams():
    print("Téléchargement teams...")
    df = nfl.import_team_desc()
    df = _select(df, COLONNES_TEAMS, "teams")
    df.to_parquet(OUTPUT_DIR / "teams.parquet", index=False)
    print(f"  Sauvegardé : teams.parquet ({len(df)} lignes)")


if __name__ == "__main__":
    fetch_games()
    fetch_players()
    fetch_teams()