"""Verb callbacks for Nuventure, a poor man's implementation of ScummVM.

These are invoked by the text processing engine in NVGame following
parsing of input sentences in NVParser.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import sys
from nuventure import nv_print
from nuventure.actor import NVActor
from nuventure.item import NVLamp
from nuventure.errors import NVBadArgError, NVNoArgError, NVBadTargetError, NVGameStateError


def do_move(actor: NVActor, direction: str, *_) -> bool:
    try:
        return actor.move(direction)
    except NVBadArgError:
        raise


def do_look(actor: NVActor, *_) -> bool:
    """Print a description of the cell where the player is."""
    print_state = False
    if actor.location.wanted_state == "lamp_lit":
        lamp = actor.inventory.get("lamp")
        if isinstance(lamp, NVLamp) and lamp.is_lit():
            print_state = True
    actor.location.render(longp=True, statefulp=print_state)
    return True


def do_inspect(actor: NVActor, target: str, _) -> bool:
    """Inspect an item in the same cell as the player."""
    here = actor.location
    target_itm = actor.bound_world.items[target]
    if target_itm in here.items:
        target_itm.render()
        return True
    raise NVBadArgError("inspect", target)


def do_take(actor: NVActor, target: str, _) -> bool:
    """
    Take an item from the scene and put it in the player's inventory,
    if it exists in the same cell as the player.
    """
    here = actor.location
    try:
        target_itm = actor.bound_world.items.get(target, None)
        assert(target_itm.location == here)
    except (AssertionError, AttributeError):
        raise NVBadArgError("take", target) from None
    except KeyError:
        raise NVBadTargetError("take", target) from None
    return actor.add_item(target_itm)


def do_drop(actor: NVActor, target: str, _) -> bool:
    """
    Take an item from the player's inventory and place it in the cell
    where the player is.
    """
    try:
        target_itm = actor.inventory[target]
    except KeyError:
        raise NVBadArgError("drop", target)
    return actor.drop_item(target_itm)


def do_inventory(actor: NVActor, *_) -> bool:
    """
    Show the player's inventory, if there is anything in it.
    """
    if len(actor.inventory):
        nv_print("\nYour Inventory:")
        for item in actor.inventory.values():
            nv_print(item.short_render())
        return True

    raise NVNoArgError("inventory")


def do_light(actor: NVActor, target: str, _) -> bool:
    """
    Light the player's lamp, if the player has it and it is not lit.
    """
    try:
        lamp = actor.inventory[target]
        assert(isinstance(lamp, NVLamp))
    except AssertionError:
        raise NVBadArgError("light", target)
    except KeyError:
        return NVBadTargetError("light", target)

    if lamp.is_lit():
        raise NVGameStateError("light", "cannot light already lit lamp")
    else:
        lamp.use()
        return True


def do_extinguish(actor: NVActor, target, _):
    """
    Extinguish the player's lamp, if the player has it and it is lit.
    """
    try:
        lamp = actor.inventory[target]
        assert(isinstance(lamp, NVLamp))
    except AssertionError:
        raise NVBadArgError("extinguish", target)
    except KeyError:
        raise NVBadTargetError("extinguish", target)

    if not lamp.is_lit():
        raise NVGameStateError(
            "extinguish", "cannot extinguish already extinguished lamp")
    else:
        lamp.use()
        return True


def do_arkhtos(actor: NVActor, *_):
    world = actor.bound_world
    if world.nodes["DEST"].visitedp:
        msg = """You have won!  Please visit https://python.org to collect your prize.

Spoiler: Your prize is a free download, no strings attached, of the
Python programming language, which was used to implement this game.
"""
        nv_print(msg)
        do_quit()
    else:
        raise NVGameStateError("arkhtos", "Stop trying to cheat.")


def do_quit(*_):
    """Quit the game."""
    sys.exit(0)
