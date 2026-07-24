import duckdb

con = duckdb.connect("database/nfl.duckdb")

df = con.execute("SELECT team_abbr, team_logo_espn FROM teams LIMIT 10").fetchdf()
print(df.to_string(index=False))

nulls = con.execute(
    "SELECT COUNT(*) AS total, SUM(CASE WHEN team_logo_espn IS NULL THEN 1 ELSE 0 END) AS nulls FROM teams"
).fetchdf()
print(nulls.to_string(index=False))

con.close()