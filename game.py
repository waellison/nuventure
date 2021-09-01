"""Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

import nuventure as nv

game_world = nv.World("./test-worlds/dirtest.json")
start_node = game_world.nodes["ORIGIN"]
player = nv.Actor(game_world, start_node)
game_world.add_actor(player)
parser = nv.Parser()

player.location.render()

# TODO: The movement logic here will form the basis of the movement verb later on.
while True:
    # We can assume wolog that the current location has been visited.
    player.location.visitedp = True
    print("")
    parser.read_command(player)
