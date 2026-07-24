import nfl_data_py as nfl
from pathlib import Path

OUTPUT_DIR = Path("data/static")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SEASONS = list(range(2015, 2027))

COLONNES_ROSTERS = ["player_id", "player_name", "headshot_url"]


def fetch_rosters():
    print("Téléchargement rosters (headshots)...")
    df = nfl.import_seasonal_rosters(SEASONS)

    presentes = [c for c in COLONNES_ROSTERS if c in df.columns]
    df = df[presentes]

    # Un joueur peut apparaître plusieurs fois (une ligne par saison) :
    # on garde une seule ligne par player_id, en priorisant la plus récente
    # entrée non nulle pour headshot_url.
    df = df.dropna(subset=["headshot_url"]).drop_duplicates(subset=["player_id"], keep="last")

    output_path = OUTPUT_DIR / "rosters.parquet"
    df.to_parquet(output_path, index=False)
    print(f"  Sauvegardé : {output_path} ({len(df)} joueurs uniques avec photo)")


if __name__ == "__main__":
    fetch_rosters()