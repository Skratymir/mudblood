import os
import json

from . import player_utils

def remove_player(player_id: int, player_data_directory: str, map_data_directory) -> None:
    """Removes a player from the map"""
    # Load online players
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        currently_online = json.load(f)

    # Get player name
    player_name = currently_online[str(player_id)]

    # Load the player data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
        player_data = json.load(f)

    # Get the data of the players room
    room_data = get_room_data(map_data_directory, player_data["area"], player_data["room"])

    # Remove the player from the room
    room_data["players"][:] = [x for x in room_data["players"] if x != player_id]

    _save_room_data(map_data_directory, player_data["area"], player_data["room"], room_data)

def add_player(player_id: int, map_data_directory: str, area: str, room: str) -> None:
    """Adds a player to the player register of the specified position"""
    # Get the room data
    room_data = get_room_data(map_data_directory, area, room)

    # Add the player to the room data
    room_data["players"].append(player_id)

    _save_room_data(map_data_directory, area, room, room_data)

def _save_room_data(map_data_directory: str, area: str, room: str, room_data: dict) -> None:
    """Save the given room data to a given room in a given area"""
    with open(os.path.join(map_data_directory, f"{area}.json"), "r") as f:
        area_data = json.load(f)
    area_data["rooms"][room] = room_data
    with open(os.path.join(map_data_directory, f"{area}.json"), "w") as f:
        json.dump(area_data, f, indent=4)

def get_room_data(map_data_directory: str, area: str, room: str) -> dict:
    """Return the data of a given room in a given area"""
    # If the area does not exist, throw an error
    if not os.path.exists(os.path.join(map_data_directory, f"{area}.json")):
        raise FileNotFoundError("The given position does not exist in the map directory")

    # Return the room data stored in the file of the rooms position
    area = json.load(open(os.path.join(map_data_directory, f"{area}.json"), "r"))
    return area["rooms"][room]

def  get_area_data(map_data_directory: str, area: str) -> dict:
    """Return the data of a given area"""
    # If the area does not exist, throw an error
    if not os.path.exists(os.path.join(map_data_directory, f"{area}.json")):
        raise FileNotFoundError("The given position does not exist in the map directory")

    # Return the room data stored in the file of the rooms position
    area = json.load(open(os.path.join(map_data_directory, f"{area}.json"), "r"))
    return area
