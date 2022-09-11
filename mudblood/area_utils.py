import os
import json

from . import player_utils, exceptions

def _parse_coordinates(position: list, rooms: dict) -> list:
    """Return a converted position, adjusted for the spacing"""
    return [len(rooms) + position[0], len(rooms) + position[1]]

def _save_room_data(map_data_directory: str, area: str, room: str, room_data: dict) -> None:
    """Save the given room data to a given room in a given area"""
    with open(os.path.join(map_data_directory, f"{area}.json"), "r") as f:
        area_data = json.load(f)
    area_data["rooms"][room] = room_data
    with open(os.path.join(map_data_directory, f"{area}.json"), "w") as f:
        json.dump(area_data, f, indent=4)

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


def get_area_map(map_data_directory: str, area: str) -> list:
    rooms = get_area_data(map_data_directory, area)["rooms"]
    room_positions = [_parse_coordinates(rooms[room]["position"], rooms) for room in rooms]

    Map = []
    num = 0
    for x in range(len(rooms) * 2 + 1):
        Map.append([])
        for y in range(len(rooms) * 2 + 1):
            if ([y, x] in room_positions):
                Map[x].append(" * ")
                continue
            Map[x].append("   ")


    rooms = [[_parse_coordinates(rooms[room]["position"], rooms), rooms[room]["obvious-exits"]] for room in rooms]


    for room in rooms:
        if "east" in room[1]:
            if Map[room[0][1]][room[0][0]].endswith(" "):
                Map[room[0][1]][room[0][0]] = Map[room[0][1]][room[0][0]].removesuffix(" ") + "-"
            if Map[room[0][1]][room[0][0] + 1].startswith(" "):
                Map[room[0][1]][room[0][0] + 1] = "-" + Map[room[0][1]][room[0][0] + 1].removeprefix(" ")
        
        if "west" in room[1]:
            if Map[room[0][1]][room[0][0]].startswith(" "):
                Map[room[0][1]][room[0][0]] = "-" + Map[room[0][1]][room[0][0]].removeprefix(" ")
            if Map[room[0][1]][room[0][0] - 1].endswith(" "):
                Map[room[0][1]][room[0][0] - 1] = Map[room[0][1]][room[0][0] - 1].removesuffix(" ") + "-"


    for i in range(len(Map)):
        Map.insert(i * 2, ["   "] * len(Map[1]))
    Map = Map[1:]

    for room in rooms:
        if "north" in room[1]:
            Map[room[0][1] * 2 - 1][room[0][0]] = " | "
        if "south" in room[1]:
            Map[room[0][1] * 2 - 1][room[0][0]] = " | "

    removables = []
    for line in Map:
        if all(item == "   " for item in line):
            removables.append(line)

    for line in removables:
        Map.remove(line)

    removables = True

    for x in range(len(Map[0])):
        for i in range(len(Map)):
            if Map[i][0] != "   ":
                removables = False
        if removables:
            for line in Map:
                line.pop(0)

    removables = True

    for x in range(len(Map[0])):
        for i in range(len(Map)):
            if Map[i][-1] != "   ":
                removables = False
        if removables:
            for line in Map:
                line.pop(-1)

    return Map


def move_player(player_id: int, player_data_directory: str, map_data_directory: str, exit: str) -> None:
    """Move a player to the specified room and area"""
    # Load required data
    player_data = player_utils._get_player_data(
        player_utils._get_player_name(player_id, player_data_directory),
        player_data_directory
    )
    room_data = get_room_data(map_data_directory, player_data["area"], player_data["room"])

    # Throw error if exit doesn't exist
    if not exit in room_data["obvious-exits"]:
        raise exceptions.RoomNotFoundException(f"Exit leads to non-existent room")

    # Save updated player data
    player_data["area"] = room_data["obvious-exits"][exit]["area"]
    player_data["room"] = room_data["obvious-exits"][exit]["room"]

    # Save the new player data to update their position
    player_utils.save_player_data(
        player_utils._get_player_name(player_id, player_data_directory),
        player_data_directory,
        player_data
    )

    # Move player
    remove_player(player_id, player_data_directory, map_data_directory)
    add_player(player_id, map_data_directory, room_data["obvious-exits"][exit]["area"], room_data["obvious-exits"][exit]["room"])
