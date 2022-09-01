from . import player_utils, map

def look(player_id: str, context: str, player_data_directory: str, maps: list) -> str:
    if context == "":
        player_data = player_utils._get_player_data(player_id, player_data_directory)
        for map in maps:
            if map.name == player_data["map"]:
                room_data = map.get_room_data(player_data["room"])
                return room_data["look"]
    return None
        

def do_command(command: tuple, player_data_directory: str, maps: list) -> str:
    commands = {
        "look": look
    }

    if not command[1] in commands:
        return f"You cannot {command} right now"

    return commands[command[1]](command[0], command[2], player_data_directory, maps)
