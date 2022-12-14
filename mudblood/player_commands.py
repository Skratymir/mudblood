from . import player_utils,  area_utils
from functools import partial

def quit(player_id: int, player_data_directory: str, main):
    """Disconnects the player from the server"""
    player_utils.logout(player_id, player_data_directory)
    del main.player_states[player_id]
    main.server._handle_disconnect(player_id)
    return ""


def look(player_id: str, context: str, player_data_directory: str, map_data_directory: str) -> str:
    """Return the look data of the specified room/object"""
    # Get the player name and data
    player_name = player_utils._get_player_name(player_id, player_data_directory)
    player_data = player_utils._get_player_data(player_name, player_data_directory)

    # Get the players room data
    area = player_data["area"]
    room = player_data["room"]
    room_data = area_utils.get_room_data(map_data_directory, area, room)

    if context == "":
        look_data = "{}\n".format(room_data["look"])

        # Add objects to look data
        items = room_data["objects"]
        if len(items) > 0:
            look_data += "You can see: A {}\n".format(", a ".join(items))

        # Add NPCs to look data
        characters = room_data["characters"]
        if len(characters) > 0:
            look_data += "You can see the following characters: {}\n".format(", ".join(characters))

        # Add players to look data
        players = room_data["players"]
        players = list(map(lambda x: player_utils._get_player_name(x, player_data_directory), players))
        players.remove(player_name)
        if len(players) > 0:
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

    return look_data


def show_map(player_id: int, map_data_directory: str, player_data_directory: str, server):
    """Show the player the map of the area they are currently in"""
    # Get the players area
    area = player_utils._get_player_area(
        player_utils._get_player_name(player_id, player_data_directory),
        player_data_directory
    )

    # Get the players position
    player_position = player_utils._get_player_data(
        player_utils._get_player_name(player_id, player_data_directory),
        player_data_directory
    )["position"]
    # Send an empty string to create a spacing
    server.send_message(player_id, "")

    # For every line of the map
    for line in area_utils.get_area_map(map_data_directory, area, player_position):
        # Send the player all the values of the line joined together
        server.send_message(player_id, "".join(line))
    # Return empty string for spacing and to not throw an error
    return ""


def move_area(player_id: int, player_data_directory: str, map_data_directory: str, exit: str) -> str:
    """Move the player from one room to another using the area map model"""
    area_utils.move_player(player_id, player_data_directory, map_data_directory, exit)
    player_data = player_utils._get_player_data(
        player_utils._get_player_name(player_id, player_data_directory),
        player_data_directory
    )

    # Return the look data of the new room to tell the player that they moved
    return look(player_id, "", player_data_directory, map_data_directory)
        

def do_command(player_id: int, command: str, context: str, main) -> str:
    """Execute the command the player entered
    Requires the command, the player_data_directory and a list of all
    maps loaded on the server
    """
    # Create dict with all possible commands
    commands = {
        "look": partial(look, player_id, context, main.player_data_directory, main.map_data_directory),
        "l": partial(look, player_id, context, main.player_data_directory, main.map_data_directory),
        "quit": partial(quit, player_id, main.player_data_directory, main),
        "map": partial(show_map, player_id, main.map_data_directory, main.player_data_directory, main.server)
    }

    # Change the command to lowercase for better matching
    command = command.lower()

    # Load player data
    player_data = player_utils._get_player_data(
        player_utils._get_player_name(player_id, main.player_data_directory), main.player_data_directory
    )
    # Get room data
    room_data = area_utils.get_room_data(
        main.map_data_directory,
        player_data["area"],
        player_data["room"]
    )

    # Auto exit alias search
    exit_matches = [key for key in room_data["obvious-exits"] if key.startswith(command)]
    if exit_matches:
        if len(exit_matches) > 1:
            # If more than one exits were found, return message
            return "You have to be more specific!"
        return move_area(player_id, main.player_data_directory, main.map_data_directory, exit_matches[0])

    # If the command does not exist, return "cannot do..." message
    if not command in commands:
        return "You cannot {} right now".format(command)

    # Return the output of the command
    return commands[command]()
