import time
import logging
import datetime
import os
import json

from threading import Thread
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
        map_data_directory="./map",
        start_room={"area": "lobby", "room": "main"}
        ):
        # Set server variables
        self.player_states = {}

        self.tick_time = tick_time
        self.last_tick = time.time()
        self.player_data_directory = player_data_directory
        self.login_message = login_message
        self.server = server.MudServer()

        # If set the map up
        self.map_data_directory = map_data_directory
        self.start_room = start_room

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

        # Clear players from all areas to remove ghosts
        areas = [area for area in os.listdir(map_data_directory) if area.endswith(".json")]
        for area in areas:
            area_data = json.load(open(os.path.join(map_data_directory, area), "r"))
            for room in area_data["rooms"]:
                area_data["rooms"][room]["players"] = []
            json.dump(area_data, open(os.path.join(map_data_directory, area), "w"), indent=4)

        logging.info("Server started")

    def update(self) -> None:
        """If the time that has passed since the last update
        is larger than the tick_time update"""
        if time.time() - self.last_tick > self.tick_time:
            self.server.update()
            self.last_tick = time.time()

            # Connect new players
            for player_id in self.server.get_new_players():

                # Set player state up for login
                self.player_states[player_id] = {}
                self.player_states[player_id]["login"] = codes.NOT_LOGGED_IN

                # Handle player login
                Thread(target=player_utils.handle_login, args=([
                    player_id,
                    self.player_data_directory,
                    self.map_data_directory,
                    self.start_room["area"],
                    self.start_room["room"],
                    self
                ])).start()
                logging.info(f"Player with id {player_id} has connected to the server")

            # Remove disconnected players
            for player_id in self.server.get_disconnected_players():
                # If the player wasn't currently creating an account
                # remove player from map
                if player_id in self.player_states:
                    if self.player_states[player_id]["login"] == codes.LOGGED_IN:
                        player_area = player_utils._get_player_area(
                            player_utils._get_player_name(player_id, self.player_data_directory),
                            self.player_data_directory
                        )

                        # Remove the player from the map
                        areas = [f.removesuffix(".json") for f in os.listdir(self.map_data_directory) if os.path.isfile(os.path.join(self.map_data_directory, f))]
                        for area in areas:
                            if area == player_area:
                                area_utils.remove_player(player_id, self.player_data_directory, self.map_data_directory)

                        player_utils.logout(player_id, self.player_data_directory)

                    # Remove player from player states to save memory
                    del self.player_states[player_id]

                logging.info(f"Player with id {player_id} has disconnected from the server")

            # Repeat for command since last tick
            for command in self.server.get_commands():
                # Turn the command list into seperate vars for readability and ease of use
                player_id, command, context = command

                if self.player_states[player_id]["login"] == codes.NOT_LOGGED_IN:
                    continue

                else:
                    # If the player doesn't want to log in, execute their command
                    command_output = player_commands.do_command(
                        player_id=player_id,
                        command=command,
                        context=context,
                        main=self
                    )
                    self.server.send_message(player_id, command_output)
                logging.info(
                    "Player with id {} has executed command {} {}".format(
                        player_id, command, context
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
