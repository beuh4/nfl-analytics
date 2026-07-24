import duckdb

con = duckdb.connect("database/nfl.duckdb")

query = """
    SELECT
        season,
        COUNT(*) AS total,
        SUM(CASE WHEN was_pressure IS NULL THEN 1 ELSE 0 END) AS nulls
    FROM plays
    GROUP BY season
    ORDER BY season
"""

df = con.execute(query).fetchdf()
print(df.to_string(index=False))

con.close()