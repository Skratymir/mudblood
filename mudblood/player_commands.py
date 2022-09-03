from . import player_utils, map, map_utils
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
                room_data = map_utils.get_room_data(map.map_directory, player_data["room"])
                look_data = "{}\n".format(room_data["look"])

                # If there are any visible exits, show them to the player
                if not len(room_data["obvious-exits"]) == 0:
                    look_data += "You can see the following exits: {}".format(", ".join(room_data["obvious-exits"]))
                # If there aren't, tell the player
                else:
                    look_data += """There aren't any obvious exits!
                    You might be able to find one by interacting with the room though, so don't give up!"""
                return look_data
    # Return string if no return was executed prior
    return "This hasn't been implemented yet (sry)"

def do_command(command: dict, player_data_directory: str, maps: list) -> str:
    """Execute the command the player entered
    Requires the command, the player_data_directory and a list of all
    maps loaded on the server
    """
    # Create dict with all possible commands
    commands = {
        "look": partial(look, command["player_id"], command["context"], player_data_directory, maps),
    }

    # If the command does not exist, return "cannot do..." message
    if not command["command"] in commands:
        return "You cannot {} right now".format(command["command"])

    # Return the output of the command
    return commands[command["command"]]()
