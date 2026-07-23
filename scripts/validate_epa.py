import duckdb

con = duckdb.connect("database/nfl.duckdb")

query = "SELECT posteam, COUNT(*) AS nb_plays, ROUND(AVG(epa), 4) AS epa_par_play FROM plays WHERE season = 2023 AND play_type IN ('pass', 'run') AND posteam IS NOT NULL GROUP BY posteam ORDER BY epa_par_play DESC"

result = con.execute(query).fetchdf()
print(result.to_string(index=False))

con.close()