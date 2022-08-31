import json
import os

from . import map_utils

class Map():
    def __init__(self, map_directory: str, player_data_directory: str) -> None:
        if not os.path.exists(map_directory) and os.path.isdir(map_directory):
            raise TypeError("map_directory is not a directory or doesn't exist.")
        self.map_directory = os.path.abspath(map_directory)
        if not os.path.exists(player_data_directory) and os.path.isdir(player_data_directory):
            raise TypeError("player_data_directory is not a directory or doesn't exist.")
        self.player_data_directory = os.path.abspath(player_data_directory)

    def get_room_data(self, position: list) -> dict:
        """
        Returns all data of the room at the specifed position
        """
        position = map_utils._parse_position(position)
        if not os.path.exists(os.path.join(self.map_directory, f"{position}.json")):
            raise FileNotFoundError("The given position does not exist in the map directory")
        room = json.load(open(os.path.join(self.map_directory, f"{position}.json"), "r"))
        return room

    def add_player(self, player_id: str, position: list) -> None:
        """
        Adds a player to the player register of the specified position
        """
        position = map_utils._parse_position(position)
        if not os.path.exists(os.path.join(self.map_directory, f"{position}.json")):
            raise FileNotFoundError("The given position does not exist in the map directory")
        room = json.load(open(os.path.join(self.map_directory, f"{position}.json"), "r"))
        room["players"].append(player_id)
        with open(os.path.join(self.map_directory, f"{position}.json"), "w") as f:
            json.dump(room, f)

    def remove_player(self, player_id: str) -> None:
        """
        Removes a player from the map
        """
        with open(os.path.join(self.player_data_directory, f"{player_id}.json"), "r") as f:
            player_data = json.load(f)
            player_room = map_utils._parse_position(player_data["room"])
            with open(os.path.join(self.map_directory, f"{player_room}.json"), "r") as room:
                room_data = json.load(room)
                room_data["players"][:] = [x for x in room_data["players"] if x != player_id]
            with open(os.path.join(self.map_directory, f"{player_room}.json"), "w") as room:
                json.dump(room_data, room)
