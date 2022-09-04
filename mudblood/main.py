import time
import logging
import datetime
import os

from . import *

class Server():
    """The main class of the mudblood library
    Create a server module to launch a server.
    """
    def __init__(
        self, 
        tick_time=0.5,
        log_formatter=logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s"),
        file_logger=False,
        console_logger=True,
        player_data_directory="./players",
        login_message="Logged in!",
        map_type="map"
        ):
        # Set server variables
        self.player_states = {}

        self.tick_time = tick_time
        self.last_tick = time.time()
        self.player_data_directory = player_data_directory
        self.map_type = map_type
        self.login_message = login_message
        self.server = server.MudServer()

        if map_type == "map":
            self.maps = []

        # Set the logging up
        log_formatter
        logging.root.setLevel(logging.INFO)
        root_logger = logging.getLogger()

        if file_logger:
            file_handler = logging.FileHandler("{0}/{1}.log".format("./logs", datetime.now().strftime("%d%m%Y-%H%M")))
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)

        if console_logger:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            root_logger.addHandler(console_handler)

        # Clear list of online players
        with open(os.path.join(player_data_directory, "online.json"), "w") as f:
            f.write("{}")

        logging.info("Server started")
    
    def add_map(self, map_name: str, map_data_directory: str) -> None:
        """Add a map to the server"""
        self.maps.append(map.Map(map_data_directory, self.player_data_directory, map_name))

    def update(self) -> None:
        """If the time that has passed since the last update
        is larger than the tick_time update"""
        if time.time() - self.last_tick > self.tick_time:
            self.server.update()
            self.last_tick = time.time()

            # Connect new players
            for player_id in self.server.get_new_players():
                self.player_states["login"][player_id] = codes.NOT_LOGGED_IN
                self.server.send_message(player_id, "Connected!")
                logging.info(f"Player with id {player_id} has connected to the server")

            # Remove disconnected players
            for player_id in self.server.get_disconnected_players():
                # If the player wasn't currently creating an account
                # remove player from map
                if self.player_states["login"][player_id] == codes.LOGGED_IN:
                    if self.map_type == "map":
                        player_map = player_utils._get_player_map(
                            player_utils._get_player_name(player_id, self.player_data_directory),
                            self.player_data_directory
                        )
                        for map_name in self.maps:
                            if map_name.name == player_map:
                                map_name.remove_player(player_id)

                    player_utils.save_player_data(player_id, self.player_data_directory)
                    player_utils.logout(player_id, self.player_data_directory)

                # Otherwise remove player from new logins to save memory
                del self.player_states["login"][player_id]

                logging.info(f"Player with id {player_id} has disconnected from the server")

            # Repeat for command since last tick
            for command in self.server.get_commands():
                # Turn the command list into a dict of readability and ease of use
                command = {
                    "player_id": command[0],
                    "command": command[1],
                    "context": command[2]
                }
                # If the player wants to log in, intercept the command
                if command["command"] == "login":
                    # If the player didn't enter both a name and password tell
                    # Them they did something wrong
                    if not len(command["context"].split(" ")) == 2:
                        self.server.send_message(command["player_id"],
                        "You need to log in with your account name and password!")
                        # Continue with next command
                        continue
                    # If the player has specified a name and password they want to
                    # Log in with, get the login code with those credentials
                    login = player_utils.login(command["player_id"], command["context"], self.player_data_directory)
                    # If the player wants to create a new account, do so
                    if login["code"] == codes.NEW_LOGIN:
                        # Add the player to a list of players who need to confirm their
                        # login name and password
                        if not self.player_states["login"][command["player_id"]] == codes.NOT_LOGGED_IN:
                            self.server.send_message(command["player_id"], "Please repeat your login to confirm")
                            self.player_states["login"][command["player_id"]] = login["password"]
                        # If they already are in that list and they confirmed the password, create their account
                        else:
                            if login["password"] == self.player_states["login"][command["player_id"]]:
                                player_utils.create_login(
                                    command["player_id"], 
                                    command["context"], 
                                    self.player_data_directory,
                                    self.maps[0].name
                                )
                                if self.map_type == "map":
                                    # Add the player to the default map and tell them they logged in
                                    self.maps[0].add_player(command["player_id"], [0, 0])
                                    self.player_states["login"][command["player_id"]] = codes.LOGGED_IN
                                    self.server.send_message(command["player_id"], self.login_message)
                            else:
                                # If the player entered a wrong password, tell them so
                                self.server.send_message(command["player_id"], "Passwords do not match!")

                    elif login["code"] == codes.SUCCESSFUL_LOGIN:
                        # If player logged in successfully, add them to the map and tell them they logged in
                        self.maps[0].add_player(command["player_id"], [0, 0])
                        self.server.send_message(command["player_id"], self.login_message)

                    elif login["code"] == codes.LOGIN_ERROR:
                        # If they entered the worng password, tell them so
                        self.server.send_message(command["player_id"], "Wrong password! Please try again!")

                else:
                    # If the player doesn't want to log in, execute their command
                    if self.map_type == "map":
                        command_output = player_commands.do_command(command, self.player_data_directory, self.maps)
                        self.server.send_message(command["player_id"], command_output)
                    logging.info(
                        "Player with id {} has executed command {} {}".format(
                            command["player_id"], command["command"], command["context"]
                        )
                    )
        else:
            # If the tick time isn't over yet, suspend the server for x time to
            # keep the CPU from maxing out
            time.sleep(0.1)

    def force_update(self) -> None:
        """Update the server even if the time since the last
        update is less than the tick_time"""
        self.server.update()
