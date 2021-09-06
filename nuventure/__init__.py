"""Nuventure: A poor man's ScummVM, minus the Z-code.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import sys


DIRECTIONS = {"east", "down", "up", "north", "west", "south"}

if __name__ == "__main__":
    print("this script is not runnable separately", file=sys.stderr)
    sys.exit(1)
