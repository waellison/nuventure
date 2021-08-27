"""Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

import nuventure
import textwrap

game_world = nuventure.world.World("./test-worlds/dirtest.json")
start_node = game_world.nodes["ORIGIN"]
player = nuventure.actor.Actor(game_world, start_node)

# TODO: The movement logic here will form the basis of the movement verb later on.
while True:
    print(player.location.friendly_name + "\n")
    desclength = "long" if player.location.visitedp is False else "short"
    description = player.location.describe(desclength)
    print(*textwrap.wrap(description, width=72), sep="\n")

    # We can assume wolog that the current location has been visited.
    player.location.visitedp = True
    print("")

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
