import nfl_data_py as nfl
from pathlib import Path

SEASONS = list(range(2015, 2026))  # 2015 à 2026  

COLONNES_PLAYS = [
    "play_id", "game_id", "season", "week", "season_type",
    "posteam", "defteam", "posteam_type", "home_team", "away_team",
    "down", "ydstogo", "yardline_100", "goal_to_go",
    "qtr", "game_half", "game_seconds_remaining", "half_seconds_remaining", "quarter_seconds_remaining",
    "score_differential",
    "play_type", "pass", "rush", "qb_dropback", "qb_kneel", "qb_spike", "aborted_play",
    "epa", "qb_epa", "success", "wp", "wpa", "ep",
    "complete_pass", "incomplete_pass", "interception",
    "air_yards", "yards_after_catch", "air_epa", "yac_epa",
    "pass_location", "pass_length", "cp", "cpoe",
    "rushing_yards", "run_location", "run_gap", "qb_scramble",
    "defense_coverage_type", "defense_man_zone_type", "was_pressure",
    "qb_hit", "sack", "number_of_pass_rushers", "defenders_in_box",
    "shotgun", "no_huddle", "offense_formation", "offense_personnel", "defense_personnel",
    "passer_player_id", "passer_player_name",
    "rusher_player_id", "rusher_player_name",
    "receiver_player_id", "receiver_player_name",
    "yards_gained", "touchdown", "first_down",
    "passing_yards", "receiving_yards", 
    "fumble", "fumble_lost",
    "penalty", "penalty_team", "penalty_yards",
    "solo_tackle_1_player_id", "solo_tackle_1_player_name",
    "solo_tackle_2_player_id", "solo_tackle_2_player_name",
    "assist_tackle_1_player_id", "assist_tackle_1_player_name",
    "assist_tackle_2_player_id", "assist_tackle_2_player_name",
    "assist_tackle_3_player_id", "assist_tackle_3_player_name",
    "assist_tackle_4_player_id", "assist_tackle_4_player_name",
    "tackle_for_loss_1_player_id", "tackle_for_loss_1_player_name",
    "tackle_for_loss_2_player_id", "tackle_for_loss_2_player_name",
    "sack_player_id", "sack_player_name",
    "half_sack_1_player_id", "half_sack_1_player_name",
    "half_sack_2_player_id", "half_sack_2_player_name",
    "qb_hit_1_player_id", "qb_hit_1_player_name",
    "qb_hit_2_player_id", "qb_hit_2_player_name",
    "interception_player_id", "interception_player_name",
    "pass_defense_1_player_id", "pass_defense_1_player_name",
    "pass_defense_2_player_id", "pass_defense_2_player_name",
    "forced_fumble_player_1_player_id", "forced_fumble_player_1_player_name",
    "forced_fumble_player_2_player_id", "forced_fumble_player_2_player_name",
    "desc",
    "drive", "drive_play_count", "fixed_drive_result",
    "drive_start_yard_line", "drive_time_of_possession",
    "drive_ended_with_score", "drive_inside20",
    "total_home_score", "total_away_score",
]

COLONNES_PLAYS = list(dict.fromkeys(COLONNES_PLAYS))

OUTPUT_DIR = Path("data/seasons")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_season(season: int) -> None:
    print(f"Téléchargement saison {season}...")
    df = nfl.import_pbp_data([season])

    presentes = [c for c in COLONNES_PLAYS if c in df.columns]
    absentes = [c for c in COLONNES_PLAYS if c not in df.columns]
    if absentes:
        print(f"  Colonnes absentes pour {season} : {absentes}")

    df = df[presentes]

    output_path = OUTPUT_DIR / f"{season}.parquet"
    df.to_parquet(output_path, index=False)
    print(f"  Sauvegardé : {output_path} ({len(df)} lignes)")


if __name__ == "__main__":
    for season in SEASONS:
        fetch_season(season)