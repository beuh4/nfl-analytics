# Pipeline d'ingestion — ordre d'exécution

Ces scripts reconstruisent `database/nfl.duckdb` à partir des sources
nflverse. À exécuter **dans cet ordre**, depuis la racine du projet :

```powershell
python scripts/fetch_static.py
python scripts/fetch_rosters.py
python scripts/fetch_plays.py
python scripts/load_duckdb.py
python scripts/validate_epa.py
```

## Détail de chaque étape

1. **fetch_static.py** — télécharge `games` (calendrier, scores), `players`
   (référentiel d'identifiants) et `teams` (couleurs, logos). Rapide.

2. **fetch_rosters.py** — télécharge les rosters saison par saison (bio,
   photo). Nécessaire pour les pages joueurs et les cartes Social Cards.

3. **fetch_plays.py** — télécharge le play-by-play complet, saison par
   saison. **L'étape la plus longue** (plusieurs minutes) — c'est la
   table `plays`, source de vérité de toute l'app.

4. **load_duckdb.py** — charge tous les fichiers `.parquet` produits par
   les trois scripts précédents dans `database/nfl.duckdb`. Rapide.

5. **validate_epa.py** — vérifie que les EPA calculés sur une saison
   connue correspondent à un classement d'équipes plausible (contrôle de
   cohérence, pas une étape obligatoire du pipeline).

## Changement de saison (nouvelle saison NFL en septembre)

Toutes les plages de saisons (`SEASONS = list(range(...))`) sont pilotées
par `app/constants.py` — `FIRST_SEASON` et `CURRENT_SEASON`. Changer
`CURRENT_SEASON` à cet endroit suffit ; les 3 scripts de fetch se
resynchronisent automatiquement, ce qui évite la dérive trouvée lors de
l'audit (`fetch_plays.py` et `fetch_static.py` s'étaient arrêtés à 2025
pendant que `fetch_rosters.py` allait déjà jusqu'à 2026 — chacun avait
son propre `range()` codé en dur, jamais mis à jour ensemble).

## Scripts de diagnostic (`check_*.py`, `validate_*.py`)

Pas partie du pipeline régulier — utilisés ponctuellement pendant le
développement pour vérifier une hypothèse sur les données (colonnes
disponibles, couleurs d'équipe, cohérence des logos...). Peuvent être
ignorés en usage normal.
