import time
import logging
import datetime

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
        login_message="Logged in!"
        ):
        # Set server variables
        self.new_logins = {}

        self.tick_time = tick_time
        self.last_tick = time.time()

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

        self.player_data_directory = player_data_directory

        self.login_message = login_message

        self.maps = []

        self.server = server.MudServer()
    
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
                self.server.send_message(player_id, "Connected!")
                logging.info(f"Player with id {player_id} has connected to the server")

            # Remove disconnected players
            for player_id in self.server.get_disconnected_players():
                # If the player wasn't currently creating an account
                # remove player from map
                if not player_id in self.new_logins:
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
                else:
                    del self.new_logins[player_id]

                logging.info(f"Player with id {player_id} has disconnected from the server")

            for command in self.server.get_commands():
                command = {
                    "player_id": command[0],
                    "command": command[1],
                    "context": command[2]
                }
                if command["command"] == "login":
                    if not len(command["context"].split(" ")) == 2:
                        self.server.send_message(command["player_id"],
                        "You need to log in with your account name and password!")
                        continue
                    login = player_utils.login(command["player_id"], command["context"], self.player_data_directory)
                    if login["code"] == return_codes.NEW_LOGIN:
                        if not command["player_id"] in self.new_logins:
                            self.server.send_message(command["player_id"], "Please repeat your login to confirm")
                            self.new_logins[command["player_id"]] = login["password"]
                        else:
                            if login["password"] == self.new_logins[command["player_id"]]:
                                player_utils.create_login(
                                    command["player_id"], 
                                    command["context"], 
                                    self.player_data_directory,
                                    self.maps[0].name
                                )
                                self.maps[0].add_player(command["player_id"], [0, 0])
                                self.server.send_message(command["player_id"], self.login_message)
                            else:
                                self.server.send_message(command["player_id"], "Passwords do not match!")
                            del self.new_logins[command["player_id"]]

                    elif login["code"] == return_codes.SUCCESSFULL_LOGIN:
                        self.maps[0].add_player(command["player_id"], [0, 0])
                        self.server.send_message(command["player_id"], self.login_message)

                    elif login["code"] == return_codes.LOGIN_ERROR:
                        self.server.send_message(command["player_id"], "Wrong password! Please try again!")

                else:
                    command_output = player_commands.do_command(command, self.player_data_directory, self.maps)
                    self.server.send_message(command["player_id"], command_output)
                    logging.info(
                        "Player with id {} has executed command {} {}".format(
                            command["player_id"], command["command"], command["context"]
                        )
                    )
        else:
            time.sleep(0.1)

    def force_update(self) -> None:
        """Update the server even if the time since the last
        update is less than the tick_time"""
        self.server.update()