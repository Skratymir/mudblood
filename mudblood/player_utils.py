import os
import json
import hashlib

from .codes import *

def _get_player_data(player_name: str, player_data_directory: str) -> dict:
    """Return playerdata"""
    # If the players data does not exist, raise error
    if not os.path.exists(os.path.join(player_data_directory, f"{player_name}.json")):
        raise FileNotFoundError(f"Player data of player_id {player_name} not found in {player_data_directory}")
    
    # Return player data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
        return json.load(f)

def _get_player_name(player_id: int, player_data_directory: str) -> str:
    """Return the player name"""
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        online_players = json.load(f)
    return online_players[str(player_id)]

def _get_player_map(player_name: str, player_data_directory: str) -> str:
    """Return the map the player is currently on"""
    player_data = _get_player_data(player_name, player_data_directory)
    return player_data["map"]

def _get_player_area(player_name: str, player_data_directory: str) -> str:
    player_data = _get_player_data(player_name, player_data_directory)
    return player_data["area"]

def get_online_players(player_data_directory: str) -> dict:
    """Return the dict of online players and their IDs"""
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        return json.load(f)

def save_player_data(player_id: int, player_data_directory: str) -> None:
    """Save the data of a player"""
    # Load the player name and data
    player_name = _get_player_name(player_id, player_data_directory)
    player_data = _get_player_data(player_name, player_data_directory)
    # Save the data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "w") as f:
        json.dump(player_data, f, indent=4)

def login(player_id: int, login_data: str, player_data_directory: str) -> dict:
    """Handle a login attempt"""
    # Split the name and password into two vars
    player_name, password = login_data.split(" ")

    # If there is not account with the players name
    if not os.path.exists(os.path.join(player_data_directory, f"{player_name}.json")):
        # Return the NEW_LOGIN code and their password
        return {
            "code": NEW_LOGIN,
            "password": password
        }
    # If the player already has an account
    else:
        # Load their player data
        with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
            player_data = json.load(f)

        # Check if they entered the correct password
        if hashlib.md5(password.encode()).hexdigest() == player_data["password-hash"]:
            # If they entered the correct password, log them in and return a successfull login
            _add_login(player_id, player_name, player_data_directory)
            return {
                "code": SUCCESSFUL_LOGIN
            }

        # If the player has entered a wrong password, return a LOGIN_ERROR
        else:
            return {
                "code": LOGIN_ERROR
            }

def create_login(player_id: int, login_data: str, player_data_directory: str, map_name: str) -> dict:
    """Create a new account"""
    # Split the players name and password into two vars
    player_name, password = login_data.split(" ")

    # Hash the password
    password = hashlib.md5(password.encode())

    # Create the player data
    player_data = {
        "room": [0, 0],
        "map": map_name,
        "password-hash": password.hexdigest()
    }
    # Save the player data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "w") as f:
        json.dump(player_data, f, indent=4)

    # Add the player to the logged in players
    _add_login(player_id, player_name, player_data_directory)

def logout(player_id: str, player_data_directory: str) -> None:
    """Remove player from the list of online players"""
    # Load currently online players
    currently_online = get_online_players(player_data_directory)
    
    # Remove player from currently online players
    del currently_online[str(player_id)]

    # Save currently online players
    with open(os.path.join(player_data_directory, "online.json"), "w") as f:
        json.dump(currently_online, f, indent=4)

def _add_login(player_id: int, player_name: str, player_data_directory: str) -> None:
    """Add a player to the list of online players"""
    
    # Load currently online players
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        currently_online = json.load(f)
    
    # Add player to currently online players and bind 
    # player_id to player name (For this session)
    currently_online[player_id] = player_name

    # Save currently online players
    with open(os.path.join(player_data_directory, "online.json"), "w") as f:
        json.dump(currently_online, f, indent=4)
