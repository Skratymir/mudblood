"""
The map module of the mudblood MUD library.

Contains one main class Map() to create a map instance (you can have multiple maps).
The Map class contains functions to handle events which influence the map.
"""

import json
import os

from . import map_utils

class Map():
    """The Map class to create maps and worlds in your MUD

    The Map requires a map_directory to store all rooms and their items, objects, etc.
    It also requires a player_data_directory to store player data like the name,
    level, equip, etc 
    """
    def __init__(self, map_directory: str, player_data_directory: str) -> None:
        # Check if the given map_directory exists and then adds it to the instance vars
        if not os.path.exists(map_directory) and os.path.isdir(map_directory):
            raise TypeError("map_directory is not a directory or doesn't exist.")
        self.map_directory = os.path.abspath(map_directory)
        # Check if the given player_data_directory exists and then adds it to the instance vars
        if not os.path.exists(player_data_directory) and os.path.isdir(player_data_directory):
            raise TypeError("player_data_directory is not a directory or doesn't exist.")
        self.player_data_directory = os.path.abspath(player_data_directory)

    def get_room_data(self, position: list) -> dict:
        """
        Returns all data of the room at the specifed position
        """
        # Converts the list position into a string position
        position = map_utils._parse_position(position)
        # If the room at the position does not exist, throw an error
        if not os.path.exists(os.path.join(self.map_directory, f"{position}.json")):
            raise FileNotFoundError("The given position does not exist in the map directory")
        # Return the room data stored in the file of the rooms position
        room = json.load(open(os.path.join(self.map_directory, f"{position}.json"), "r"))
        return room

    def add_player(self, player_id: str, position: list) -> None:
        """
        Adds a player to the player register of the specified position
        """
        # Get the room data
        room = self.get_room_data(position)
        # Add the player to the room data
        room["players"].append(player_id)
        # Save the room data
        with open(os.path.join(self.map_directory, f"{position}.json"), "w") as f:
            json.dump(room, f)

    def remove_player(self, player_id: str) -> None:
        """
        Removes a player from the map
        """
        # Load the player data
        with open(os.path.join(self.player_data_directory, f"{player_id}.json"), "r") as f:
            player_data = json.load(f)
            # Get the data of the players room
            room_data = self.get_room_data(player_data["room"])
            player_room = room_data["room"]
            # Remove the player from the room
            room_data["players"][:] = [x for x in room_data["players"] if x != player_id]
            # Save the data
            with open(os.path.join(self.map_directory, f"{player_room}.json"), "w") as room:
                json.dump(room_data, room)
