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
from . import nv_print
from .parser import NVVerb
from .item import NVLamp
from .errors import NVBadArgError, NVNoArgError, NVBadTargetError, NVGameStateError


def do_move(verb: NVVerb) -> bool:
    """Attempt to move the given character in the specified direction."""
    try:
        return verb.invoker.move(verb.target)
    except NVBadArgError:
        raise


def do_look(verb: NVVerb) -> bool:
    """Print a description of the cell where the player is."""
    print_state = False
    if verb.invoker.location.wanted_state == "lamp_lit":
        lamp = verb.invoker.inventory.get("lamp")
        if isinstance(lamp, NVLamp) and lamp.is_lit():
            print_state = True
    verb.invoker.location.render(long_p=True, stateful_p=print_state)
    return True


def do_inspect(verb: NVVerb) -> bool:
    """Inspect an item in the same cell as the player."""
    here = verb.invoker.location
    target_itm = verb.invoker.bound_world.items[verb.target]
    if target_itm in here.items:
        target_itm.render()
        return True
    raise NVBadArgError("inspect", verb.target)


def do_take(actor, target: str, _) -> bool:
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


def do_drop(actor, target: str, _) -> bool:
    """
    Take an item from the player's inventory and place it in the cell
    where the player is.
    """
    try:
        target_itm = actor.inventory[target]
    except KeyError:
        raise NVBadArgError("drop", target)
    return actor.drop_item(target_itm)


def do_inventory(actor, *_) -> bool:
    """
    Show the player's inventory, if there is anything in it.
    """
    if actor.inventory:
        nv_print("\nYour Inventory:")
        _ = [nv_print(item.short_render) for item in actor.inventory.values()]
        return True

    raise NVNoArgError("inventory")


def do_light(verb: NVVerb) -> bool:
    """
    Light the player's lamp, if the player has it and it is not lit.
    """
    try:
        lamp = verb.invoker.inventory[verb.target]
        assert(isinstance(lamp, NVLamp))
    except AssertionError:
        raise NVBadArgError("light", verb.target)
    except KeyError:
        raise NVBadTargetError("light", verb.target)

    if lamp.is_lit():
        raise NVGameStateError("light")
    else:
        lamp.use()
        return True


def do_extinguish(verb: NVVerb) -> bool:
    """
    Extinguish the player's lamp, if the player has it and it is lit.
    """
    try:
        lamp = verb.invoker.inventory[verb.target]
        assert(isinstance(lamp, NVLamp))
    except AssertionError:
        raise NVBadArgError("extinguish", verb.target)
    except KeyError:
        raise NVBadTargetError("extinguish", verb.target)

    if not lamp.is_lit():
        raise NVGameStateError("extinguish")
    else:
        lamp.use()
        return True


def do_arkhtos(verb: NVVerb) -> None:
    """Trigger the game's win condition."""
    world = verb.invoker.bound_world
    if world.nodes["DEST"].visited_p:
        msg = """You have won!  Please visit https://python.org to collect your prize.

Spoiler: Your prize is a free download, no strings attached, of the
Python programming language, which was used to implement this game.
"""
        nv_print(msg)
        do_quit()
    else:
        raise NVGameStateError("arkhtos")


def do_quit(*_) -> None:
    """Quit the game."""
    sys.exit(0)
