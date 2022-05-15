"""Nuventure: A text-based adventure game engine written in Python.

William Ellison <waellison@gmail.com>
https://github.com/tnwae/nuventure
"""

from nuventure import dbg_print
from nuventure.game import NVGame

dbg_print("main", "this is Nuventure v0.1")

GAME = NVGame("./test-worlds/dirtest.json")
GAME.run()
