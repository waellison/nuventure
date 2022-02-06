"""Nuventure: A poor man's ScummVM, minus the Z-code.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import sys
import textwrap

"""The permissible directions of travel within the Nuventure engine."""
DIRECTIONS = {"east", "down", "up", "north", "west", "south"}

"""The default error string for parse errors."""
ERROR_STR = "Huh?"

"""Whether debug output should be enabled."""
DEBUG_MODE = False


def nv_print(text, width=72):
    """Pretty-print long text to a narrow screen (default width: 72 chars)."""
    print(*textwrap.wrap(text, width), sep="\n")


def func_name():
    """Return the name of the function we are currently in."""
    return sys._getframe().f_back.f_code.co_name


def dbg_print(funcname, *args):
    """
    Print debug output, if debugging is enabled.

    Args:
        funcname: name of the calling function
        *args: one or more strings to print
    """
    if DEBUG_MODE:
        print(f"{funcname}:", *args)


if __name__ == "__main__":
    print("this script is not runnable separately", file=sys.stderr)
    sys.exit(1)
