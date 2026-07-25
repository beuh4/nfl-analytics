import nfl_data_py as nfl
import duckdb

df = nfl.import_seasonal_rosters(list(range(2015, 2027)))

print(f"Lignes roster (toutes saisons) : {len(df)}")
print(f"Joueurs uniques (player_id) : {df['player_id'].nunique()}")
print()

roster_ids = set(df["player_id"].dropna().tolist())

con = duckdb.connect("database/nfl.duckdb")
plays_ids_all = con.execute(
    "SELECT DISTINCT passer_player_id FROM plays WHERE passer_player_id IS NOT NULL"
).fetchdf()["passer_player_id"].tolist()
con.close()

matches = sum(1 for pid in plays_ids_all if pid in roster_ids)
print(f"Correspondances trouvées : {matches} / {len(plays_ids_all)} identifiants QB uniques")