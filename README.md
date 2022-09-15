# mudblood
![GitHub milestone](https://img.shields.io/github/milestones/progress-percent/Skratymir/mudblood/1?style=for-the-badge)

## What is mudblood
Mudblood is a simple library to create MUD (Multi User Dungeon) games. It enables creative persons to create their own universe, filled with magic spells, futuristic robots, or whatever you can imagine.
And you don't have to be good at coding to do it.

## No coding required?
#### Almost.
The minimal setup looks like this:
~~~python
import mudblood
server = mudblood.main.Server()
while True:
    server.update()
~~~
Within just four lines of code, you can create your very own Multi User Dungeon game. 

At least coding-wise.

## Setup Guide
To tweak your server settings, such as the tick time, you can either reference the server class
~~~python
server.tick_time = 0.5
~~~
Or set the setting while initiating the server
~~~python
server = mudblood.main.server(tick_time=0.5)
~~~

The Map system of mudblood is split into multiple areas. Those are recommended (But not required!) to be rather small, and not an entire map. Instead, the player can traverse the areas using exits located in every room. This leads to better server performance, as well as player experience.

These areas are JSON files contained within a map folder. The default name for that folder is "map", but you can change it to whatever you want.
For some info on how those files are laid out, please look at the examples provided (WIP).

You also need a player data directory. The default is "players", but again, you can change that to whatever you want. Each player will have their own JSON file which includes their location and password. The password is being hashed during account creation and cannot be accessed. Player verification works by comparing the entered password with the saved hash. The password itself is never saved.

There are a ton of other settings and features for you to configure, but those are the two required ones. For a full list of features, settings, and guides, check out the full documentation at (Full documentation coming soon)