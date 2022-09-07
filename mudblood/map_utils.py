import os
import json

def _parse_position(position: list) -> str:
    """Convert list position into string position"""
    return f"{str(position[0])}-{str(position[1])}"

def get_room_data(map_directory: str, position: list) -> dict:
    """Returns all data of the room at the specifed position"""
    # Converts the list position into a string position
    position = _parse_position(position)

    # If the room at the position does not exist, throw an error
    if not os.path.exists(os.path.join(map_directory, f"{position}.json")):
        raise FileNotFoundError("The given position does not exist in the map directory")

    # Return the room data stored in the file of the rooms position
    room = json.load(open(os.path.join(map_directory, f"{position}.json"), "r"))
    return room

def _save_room_data(map_directory: str, room_data: dict, position: list) -> None:
    """Save the room data
    Requires:
    map directory, room position and room data"""
    # Save the data
    with open(os.path.join(map_directory, f"{_parse_position(position)}.json"), "w") as f:
        json.dump(room_data, f, indent=4)