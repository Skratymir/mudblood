from . import player_utils, map
from functools import partial

def look(player_id: str, context: str, player_data_directory: str, maps: list) -> str:
    """Return the look data of the specified room/object"""
    player_name = player_utils._get_player_name(player_id, player_data_directory)
    # If no object is specified return room look data
    if context == "":
        # Get the player data
        player_data = player_utils._get_player_data(player_name, player_data_directory)
        # Find the map the player is currently loaded in
        for map in maps:
            if map.name == player_data["map"]:
                # When the right map is found, return the look data
                room_data = map.get_room_data(player_data["room"])
                return room_data["look"]
    # Return string if no return was executed prior
    return "This hasn't been implemented yet (sry)"

def do_command(command: tuple, player_data_directory: str, maps: list) -> str:
    """Execute the command the player entered
    Requires the command, the player_data_directory and a list of all
    maps loaded on the server
    """
    # Create dict with all possible commands
    commands = {
        "look": partial(look, command[0], command[2], player_data_directory, maps),
    }

    # If the command does not exist, return "cannot do..." message
    if not command[1] in commands:
        return f"You cannot {command} right now"

    # Return the output of the command
    return commands[command[1]]()
