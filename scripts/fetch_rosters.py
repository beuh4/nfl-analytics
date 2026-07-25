import nfl_data_py as nfl
from pathlib import Path

OUTPUT_DIR = Path("data/static")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEASONS = list(range(2015, 2027))

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