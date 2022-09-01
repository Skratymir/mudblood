import os
import json

def _get_player_data(player_id: str, player_data_directory: str) -> dict:
    """Return playerdata"""
    if not os.path.exists(os.path.join(player_data_directory, f"{player_id}.json")):
        raise FileNotFoundError(f"Player data of player_id {player_id} not found in {player_data_directory}")
    
    with open(os.path.join(player_data_directory, f"{player_id}.json"), "r") as f:
        return json.load(f)
    