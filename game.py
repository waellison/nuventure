"""Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

from nuventure.game import NVGame

game = NVGame("./test-worlds/dirtest.json")
game.run()
