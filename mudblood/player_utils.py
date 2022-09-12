import os
import json
import hashlib
import time

from . import area_utils
from .codes import *

def _get_player_data(player_name: str, player_data_directory: str) -> dict:
    """Return playerdata"""
    # If the players data does not exist, raise error
    if not os.path.exists(os.path.join(player_data_directory, f"{player_name}.json")):
        raise FileNotFoundError(f"Player data of player_id {player_name} not found in {player_data_directory}")
    
    # Return player data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
        return json.load(f)

def _get_player_name(player_id: int, player_data_directory: str) -> str:
    """Return the player name"""
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        online_players = json.load(f)
    return online_players[str(player_id)]

def _get_player_area(player_name: str, player_data_directory: str) -> str:
    player_data = _get_player_data(player_name, player_data_directory)
    return player_data["area"]

def get_online_players(player_data_directory: str) -> dict:
    """Return the dict of online players and their IDs"""
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        return json.load(f)

def save_player_data(player_name: str, player_data_directory: str, player_data: dict) -> None:
    """Save the data of a player"""
    # Save the data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "w") as f:
        json.dump(player_data, f, indent=4)

def login(player_id: int, login_data: list, player_data_directory: str) -> dict:
    """Handle a login attempt"""
    # Split the name and password into two vars
    player_name, password = login_data

    # If there is not account with the players name
    if not os.path.exists(os.path.join(player_data_directory, f"{player_name}.json")):
        # Return the NEW_LOGIN code and their password
        return {
            "code": NEW_LOGIN,
            "password": password
        }
    # If the player already has an account
    else:
        # Load their player data
        with open(os.path.join(player_data_directory, f"{player_name}.json"), "r") as f:
            player_data = json.load(f)

        # Check if they entered the correct password
        if hashlib.md5(password.encode()).hexdigest() == player_data["password-hash"]:
            # If they entered the correct password, log them in and return a successfull login
            _add_login(player_id, player_name, player_data_directory)
            return {
                "code": SUCCESSFUL_LOGIN
            }

        # If the player has entered a wrong password, return a LOGIN_ERROR
        else:
            return {
                "code": LOGIN_ERROR
            }

def create_login(player_id: int, login_data: list, map_data_directory: str, player_data_directory: str, area_name: str, room_name: str) -> dict:
    """Create a new account"""
    # Split the players name and password into two vars
    player_name, password = login_data

    # Hash the password
    password = hashlib.md5(password.encode())

    position = area_utils.get_room_data(map_data_directory, area_name, room_name)["position"]

    # Create the player data
    player_data = {
        "room": room_name,
        "area": area_name,
        "position": position,
        "password-hash": password.hexdigest()
    }
    # Save the player data
    with open(os.path.join(player_data_directory, f"{player_name}.json"), "w") as f:
        json.dump(player_data, f, indent=4)

    # Add the player to the logged in players
    _add_login(player_id, player_name, player_data_directory)

def logout(player_id: str, player_data_directory: str) -> None:
    """Remove player from the list of online players"""
    # Load currently online players
    currently_online = get_online_players(player_data_directory)
    
    # Remove player from currently online players
    del currently_online[str(player_id)]

    # Save currently online players
    with open(os.path.join(player_data_directory, "online.json"), "w") as f:
        json.dump(currently_online, f, indent=4)

def _add_login(player_id: int, player_name: str, player_data_directory: str) -> None:
    """Add a player to the list of online players"""
    
    # Load currently online players
    with open(os.path.join(player_data_directory, "online.json"), "r") as f:
        currently_online = json.load(f)
    
    # Add player to currently online players and bind 
    # player_id to player name (For this session)
    currently_online[player_id] = player_name

    # Save currently online players
    with open(os.path.join(player_data_directory, "online.json"), "w") as f:
        json.dump(currently_online, f, indent=4)


def handle_login(player_id: int, player_data_directory: str, map_data_directory: str, spawn_area: str, spawn_room: str, main) -> None:
    """The player login thread. Handles the player login and account creation"""
    # Ask the player for their username
    main.server.send_message(player_id, "What is thy name, adventurer?")

    # Wait until the player entered something (server.update() coming from main Thread)
    commands = main.server.get_commands()
    while not any(player_id in l for l in commands):
        time.sleep(0.5)
        commands = main.server.get_commands()

    # Get the players input and set the name to it
    for command in commands:
        if command[0] == player_id:
            name = command[1]

    # Ask the player for their password
    main.server.send_message(player_id, "What is thy unlock spell, {}?".format(name))

    # Wait until the player entered something (server.update() coming from main Thread)
    commands = []    
    while not any(player_id in l for l in commands):
        time.sleep(0.5)
        commands = main.server.get_commands()

    # Get the players input and set their password to it
    for command in commands:
        if command[0] == player_id:
            password = command[1]

    # Get the login code using those credentials
    login_code = login(player_id, [name, password], player_data_directory)

    # If the player is creating a new account
    if login_code["code"] == NEW_LOGIN:
        # Ask the player to confirm their password
        main.server.send_message(player_id, "Please confirm thy unlock spell, {}.".format(name))
        # Wait for the player to enter something
        commands = []    
        while not any(player_id in l for l in commands):
            time.sleep(0.5)
            commands = main.server.get_commands()

        # Get the players input and set the password to it
        for command in commands:
            if command[0] == player_id:
                password = command[1]

        # If the player entered the same password twice
        if login_code["password"] == password:
            # Create their login, add them to the spawn room, set their player state, send them a message
            create_login(player_id, [name, password], map_data_directory, player_data_directory, spawn_area, spawn_room)
            area_utils.add_player(player_id, map_data_directory, spawn_area, spawn_room)
            main.player_states[player_id]["login"] = LOGGED_IN
            main.player_states[player_id]["game"] = IDLE
            main.server.send_message(player_id, "You are now entering another realm, adventurer. Take care on your journey!")
        # If the player entered two different passwords
        else:
            # Tell the player their password doesn't match
            main.server.send_message(player_id, "Thy spell does not match! You shall not enter!")
            # Remove the player from the server
            del main.player_states[player_id]
            main.server._handle_disconnect(player_id)

    # If the player entered the correct credentials
    elif login_code["code"] == SUCCESSFUL_LOGIN:
        # Add the player to their current room, set their player state, send them a message
        player_data = _get_player_data(_get_player_name(player_id, player_data_directory), player_data_directory)
        area_utils.add_player(player_id, map_data_directory, player_data["area"], player_data["room"])
        main.player_states[player_id]["login"] = LOGGED_IN
        main.player_states[player_id]["game"] = IDLE
        main.server.send_message(player_id, "You are now entering another realm, adventurer. Take care on your journey!")

    # If the player entered a wrong password
    elif login_code["code"] == LOGIN_ERROR:
        # Tell them they entered the wrong password
        main.server.send_message(player_id, "Thy spell is incorrect! You shall not enter!")
        # Remove the player from the server
        del main.player_states[player_id]
        main.server._handle_disconnect(player_id)
