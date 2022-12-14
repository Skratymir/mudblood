Basics
================================================================================
This chapter will teach you the very first steps to set your own MUD server up.

-----------
Server loop
-----------
To run your server, you are going to need at least two folders. You need a map folder and a player data folder.
Those folders are going to contain a lot of JSON files, some generated by the server and some created by yourself. If you delete any of the files in those directories, you server becomes vulnarable to crashes, as required data will cease to exist. If you want to delete an area from you server, you need to also remove the area from all players files (JSON files located in the player data directory).

Once you have created those two folders, you can start configuring the MUD and server themselves.
Here is an example of the most working server possible:

.. code:: python

    # Import the library
    import mudblood
    # Set your starting room
    # Replace the some-area and some-room with the area and room you want your player to spawn in!
    start_room = {"area": "some-area", "room": "some-room"}
    # Initiate the server
    server = mudblood.main.Server(start_room)
    # Start the main server loop
    while True:
        server.update()