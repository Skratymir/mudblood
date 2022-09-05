from . import player_utils, map_utils, area_utils
from functools import partial

def look(player_id: str, context: str, player_data_directory: str, maps: list, map_type: str, map_data_direcory: str) -> str:
    """Return the look data of the specified room/object"""
    if map_type == "map":
        # Get player name and data
        player_name = player_utils._get_player_name(player_id, player_data_directory)
        player_data = player_utils._get_player_data(player_name, player_data_directory)

        # Find the map the player is currently loaded in
        for map_item in maps:
            if map_item.name == player_data["map"]:
                # When the right map is found, return the room data
                room_data = map_utils.get_room_data(map_item.map_directory, player_data["room"])

        # If no object is specified return room look data
        if context == "":
            look_data = "{}\n".format(room_data["look"])

            # Add objects to look data
            items = room_data["objects"]
            look_data += "You can see: A {}\n".format(", a ".join(items))

            # Add NPCs to look data
            characters = room_data["characters"]
            look_data += "You can see the following characters: {}\n".format(", ".join(characters))

            # Add players to look data
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
    
    elif map_type == "area":
        # Get the player name and data
        player_name = player_utils._get_player_name(player_id, player_data_directory)
        player_data = player_utils._get_player_data(player_name, player_data_directory)

        # Get the players room data
        area = player_data["area"]
        room = player_data["room"]
        room_data = area_utils.get_room_data(map_data_direcory, area, room)

        if context == "":
            look_data = "{}\n".format(room_data["look"])

            look_data += "You can see: A {}\n".format(", a ".join(room_data["objects"]))

            # Add NPCs to look data
            characters = room_data["characters"]
            look_data += "You can see the following characters: {}\n".format(", ".join(characters))

            # Add players to look data
            players = room_data["players"]
            players = list(map(lambda x: player_utils._get_player_name(x, player_data_directory), players))
            look_data += "You can see the following players: {}\n".format(", ".join(players))

        return look_data
        

def do_command(player_id: int, command: str, context: str, player_data_directory: str, map_type: str, maps=[], map_data_directory="") -> str:
    """Execute the command the player entered
    Requires the command, the player_data_directory and a list of all
    maps loaded on the server
    """
    # If the player is not logged in, tell them to log in
    if not str(player_id) in player_utils.get_online_players(player_data_directory):
        print(player_utils.get_online_players(player_data_directory))
        return "You need to log in!"

    # Create dict with all possible commands
    commands = {
        "look": partial(look, player_id, context, player_data_directory, maps, map_type, map_data_directory),
        "l": partial(look, player_id, context, player_data_directory, maps, map_type, map_data_directory)
    }

    # If the command does not exist, return "cannot do..." message
    if not command in commands:
        return "You cannot {} right now".format(command)

    # Return the output of the command
    return commands[command]()
