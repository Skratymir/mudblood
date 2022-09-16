Server
====================================================================
This chapter will teach you how to tweak the settings of your server

--------
Settings
--------
There are a lot of settings for you to configure to your liking. You can change those settings either when initiating the server, or on runtime.

Here is an example on how to set a setting while initiating:

.. code:: python

    server = mudblood.main.Server(start_room, tick_time=1)

However, if you want to change a setting while the server is already running, or want more readable code, you can change settings on runtime:

.. code:: python

    server = mudblood.main.Server(start_room)
    server.tick_time = 1


-------------
Settings List
-------------

- tick_time (0.5): The time between every server update in seconds. Do not use time.sleep() in your main loop, use the tick_time, to compensate for server lag.
- log_formatter (logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")): A logging.Formatter to replace the default one
- file_logger (False): If the logs are supposed to be saved into the log folder as log files
- console_logger (True): If the logging output is supposed to be written to the console
- player_data_directory ("./players"): The directory of the player data
- map_data_directory ("./map"): The directory of the area files