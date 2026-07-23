import nfl_data_py as nfl

df = nfl.import_pbp_data([2023])

print("Valeurs uniques - defense_coverage_type :")
print(df["defense_coverage_type"].value_counts(dropna=False))
print()

print("Valeurs uniques - defense_man_zone_type :")
print(df["defense_man_zone_type"].value_counts(dropna=False))
print()

print("Taux de remplissage was_pressure :")
print(df["was_pressure"].value_counts(dropna=False))
print()

print("Taux de valeurs manquantes (NaN) sur ces 3 colonnes :")
print(df[["defense_coverage_type", "defense_man_zone_type", "was_pressure"]].isna().mean())