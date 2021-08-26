"""
Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

from nuventure import world

game_world = world.World("./test-worlds/dirtest.json")

present_node = game_world.nodes["ORIGIN"]
movedp = True
directions = {"east", "down", "up", "north", "west", "south"}

# TODO: The movement logic here will form the basis of the movement verb later on.
while True:
    if movedp:
        print(present_node.friendly_name)

    try:
        direction = input("> ")
    except EOFError:
        break

    if direction == "quit":
        break
    elif not(direction in directions):
        print("bad dog")
    else:
        if direction in present_node.neighbors:
            present_node = game_world.nodes[present_node.neighbors[direction]["name"]]
            movedp = True
        else:
            print("Can't go that way.")
            movedp = False
