import json
import os

from .exceptions import FileTypeError

class Map():
    def __init__(self, map_directory: str):
        if not os.path.exists(map_directory) and os.path.isdir(map_directory):
            raise TypeError("map_directory is not a directory or doesn't exist.")
        self.map_directory = os.path.abspath(map_directory)

    def get_exits(self, position) -> list:
        """
        Return all the exits available from a given position.
        Uses the map_directory of the main Map()
        """
        if not os.path.exists(os.path.join(self.map_directory, f"{position}.json")):
            raise FileNotFoundError("The given position does not exist in the map directory")
        room = json.load(open(os.path.join(self.map_directory, f"{position}.json"), "r"))
        return room["obvious-exits"]

    def add_player(self, player_id: str, position: str) -> None:
        """
        Adds a player to the player register of the specified position
        """
        if not os.path.exists(os.path.join(self.map_directory, f"{position}.json")):
            raise FileNotFoundError("The given position does not exist in the map directory")
        room = json.load(open(os.path.join(self.map_directory, f"{position}.json"), "r"))
        room["players"].append(player_id)
        with open(os.path.join(self.map_directory, f"{position}.json"), "w") as f:
            json.dump(room, f)
