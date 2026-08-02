import nfl_data_py as nfl
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "app"))
from constants import FIRST_SEASON, CURRENT_SEASON

OUTPUT_DIR = Path("data/static")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ce script était déjà correct (allait bien jusqu'à 2026), contrairement à
# fetch_plays.py et fetch_static.py — aligné ici sur la même constante
# partagée pour que les quatre scripts ne puissent plus diverger.
SEASONS = list(range(FIRST_SEASON, CURRENT_SEASON + 1))

COLONNES_ROSTERS = [
    "player_id", "player_name", "season", "team", "position",
    "age", "height", "weight", "college", "jersey_number", "years_exp",
    "headshot_url",
]


def fetch_rosters():
    print("Téléchargement rosters (bio + headshots)...")
    df = nfl.import_seasonal_rosters(SEASONS)

    presentes = [c for c in COLONNES_ROSTERS if c in df.columns]
    absentes = [c for c in COLONNES_ROSTERS if c not in df.columns]
    if absentes:
        print(f"  Colonnes absentes : {absentes}")
    if "jersey_number" in df.columns:
        df["jersey_number"] = pd.to_numeric(df["jersey_number"], errors="coerce")
    df = df[presentes]

    # Une ligne par joueur ET par saison (pas de dédup globale par player_id) :
    # nécessaire pour connaître l'équipe/âge exacts au moment d'une saison
    # donnée, plutôt que la dernière valeur connue toutes saisons confondues.
    df = df.drop_duplicates(subset=["player_id", "season"], keep="last")

    output_path = OUTPUT_DIR / "rosters.parquet"
    df.to_parquet(output_path, index=False)
    print(f"  Sauvegardé : {output_path} ({len(df)} lignes joueur-saison)")


if __name__ == "__main__":
    fetch_rosters()