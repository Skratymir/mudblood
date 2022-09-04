from . import player_utils, map_utils
from functools import partial

def look(player_id: str, context: str, player_data_directory: str, maps: list) -> str:
    """Return the look data of the specified room/object"""
    # Get player name and data
    player_name = player_utils._get_player_name(player_id, player_data_directory)
    player_data = player_utils._get_player_data(player_name, player_data_directory)

    # Find the map the player is currently loaded in
    for map_item in maps:
        if map_item.name == player_data["map"]:
            # When the right map is found, return the look data
            room_data = map_utils.get_room_data(map_item.map_directory, player_data["room"])

    # If no object is specified return room look data
    if context == "":
        look_data = "{}\n".format(room_data["look"])

        items = room_data["objects"]
        look_data += "You can see: A {}\n".format(", a ".join(items))

        characters = room_data["characters"]
        look_data += "You can see the following characters: {}\n".format(", ".join(characters))

        players = room_data["players"]
        players = list(map(lambda x: player_utils._get_player_name(x, player_data_directory), players))
        look_data += "You can see the following players: {}\n".format(", ".join(players))

        # If there are any visible exits, show them to the player
        if not len(room_data["obvious-exits"]) == 0:
            look_data += "You can see the following exits: {}".format(", ".join(room_data["obvious-exits"]))
        # If there aren't, tell the player
        else:
            look_data += """There aren't any obvious exits!
            You might be able to find one by interacting with the room though, so don't give up!"""
        return look_data
    
    # If an object was specified
    else:
        # And exists within the room
        if context in room_data["objects"]:
            # Return the search data of the object
            look_data = "You examine the {}:\n".format(context)
            look_data += "{}".format(room_data["objects"][context]["search"])
        else:
            # If the object doesn't exist, return that
            look_data = "There is no {} here...".format(context)

        # Return the look data
        return look_data
        

def do_command(command: dict, player_data_directory: str, maps: list) -> str:
    """Execute the command the player entered
    Requires the command, the player_data_directory and a list of all
    maps loaded on the server
    """
    # If the player is not logged in, tell them to log in
    if not str(command["player_id"]) in player_utils.get_online_players(player_data_directory):
        print(player_utils.get_online_players(player_data_directory))
        return "You need to log in!"

    # Create dict with all possible commands
    commands = {
        "look": partial(look, command["player_id"], command["context"], player_data_directory, maps),
        "l": partial(look, command["player_id"], command["context"], player_data_directory, maps)
    }

    # If the command does not exist, return "cannot do..." message
    if not command["command"] in commands:
        return "You cannot {} right now".format(command["command"])

    # Return the output of the command
    return commands[command["command"]]()
