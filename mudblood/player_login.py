import os
import hashlib
import json

def login(login_data: str, player_data_directory: str) -> dict:
    login_data = login_data.split(" ")
    player_name = login_data[0]
    if not os.path.exists(os.path.join(player_data_directory, f"{player_name}.json")):
        return {
            "code": 2,
            "password": login_data[1]
        }
    else:
        with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
            player_data = json.load(f)

        if hashlib.md5(login_data[1].encode()).hexdigest() == player_data["password-hash"]:
            return {
                "code": 1
            }

def create_login(player_id: int, login_data: str, player_data_directory: str, map_name: str) -> dict:
    player_name, password = login_data.split(" ")
    password = hashlib.md5(password.encode())
    player_data = {
        "room": [0, 0],
        "map": map_name,
        "password-hash": password.hexdigest()
    }
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "w") as f:
        json.dump(player_data, f)

    _add_login(player_id, player_name, player_data_directory)

def logout(player_id: str, player_data_directory: str) -> None:
    """Remove player from the list of online players"""
    # Load currently online players
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        currently_online = json.load(f)
    
    # Remove player from currently online players
    del currently_online[str(player_id)]

    # Save currently online players
    with open(os.path.join(player_data_directory, "online.json"), "w") as f:
        json.dump(currently_online, f)

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
        json.dump(currently_online, f)
