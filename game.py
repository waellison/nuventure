"""
Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

import nuventure as nv

game_world = nv.world.World("./test-worlds/dirtest.json")
start_node = game_world.nodes["ORIGIN"]
player = nv.actor.Actor(game_world, start_node)

# TODO: The movement logic here will form the basis of the movement verb later on.
while True:
    print(player.location.friendly_name)

    try:
        direction = input("> ")
    except EOFError:
        break

    if direction == "quit":
        break
    else:
        movedp = player.move(direction)

        if movedp is True:
            continue
        elif movedp is False:
            print("Can't go that way.")
        else:
            print("Invalid command.")
