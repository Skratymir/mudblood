Map
===========================================================================
This chapter will teach you how to write JSON files to create your own map.

----------
JSON Files
----------
The map consists of many different JSON files, one file for each area.
The area consists of room, which all have players, objects and other things in them. Here is an example for a very basic area:

.. code:: JSON

    {
    "rooms": {
        "main": {
            "look": "You can see a circular plaza. You can see people arrive here seemingly out of nowhere.",
            "players": [
                0
            ],
            "objects": {
                "tree": {
                    "search": "A very fine oak tree."
                }
            },
            "characters": {
                "Draagon": {
                    "type": "dialogue",
                    "dialogue": [
                        "Hey! My name is Draagon!",
                        "Feel free to talk to me at any time!"
                    ]
                }
            },
            "obvious-exits": {
                "east": {
                    "area": "lobby",
                    "room": "forrest",
                    "position": [
                        1,
                        0
                    ]
                },
                "north": {
                    "area": "lobby",
                    "room": "trees",
                    "position": [
                        0,
                        -1
                    ]
                }
            },
            "position": [
                0,
                0
            ]
        },
        "forrest": {
            "look": "This is the text shown when the player runs \"look\"",
            "players": [],
            "objects": {},
            "characters": {},
            "obvious-exits": {
                "west": {
                    "area": "lobby",
                    "room": "main",
                    "position": [
                        0,
                        0
                    ]
                }
            },
            "position": [
                1,
                0
            ]
        }
    }