import os
import json

def _get_player_data(player_name: str, player_data_directory: str) -> dict:
    """Return playerdata"""
    # If the players data does not exist, raise error
    if not os.path.exists(os.path.join(player_data_directory, f"{player_name}.json")):
        raise FileNotFoundError(f"Player data of player_id {player_name} not found in {player_data_directory}")
    
    # Return player data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
        return json.load(f)

def _get_player_name(player_id: int, player_data_directory: str) -> str:
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        online_players = json.load(f)
    return online_players[str(player_id)]

def _get_online_players(player_data_directory: str) -> dict:
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        return json.load(f)

def save_player_data(player_id: int, player_data_directory: str) -> None:
    player_name = _get_player_name(player_id, player_data_directory)
    player_data = _get_player_data(player_name, player_data_directory)
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "w") as f:
        json.dump(player_data, f)
