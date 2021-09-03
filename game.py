"""Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

from nuventure.world import World
from nuventure.actor import Actor
from nuventure.parser import Parser, Verb

game_world = World("./test-worlds/dirtest.json")
start_node = game_world.nodes["ORIGIN"]
player = Actor(game_world, start_node)
game_world.add_actor(player)
parser = Parser()
player.location.render()

while True:
    player.location.visitedp = True
    print("")
    verb = parser.read_command(player)
    if verb:
        verb.invoke()
    else:
        print(verb)
