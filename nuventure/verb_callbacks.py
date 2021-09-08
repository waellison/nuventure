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
from nuventure.actor import NVActor
from nuventure.item import NVLamp


def do_east(actor: NVActor, *_):
    return actor.move("east")


def do_west(actor: NVActor, *_):
    return actor.move("west")


def do_north(actor: NVActor, *_):
    return actor.move("north")


def do_up(actor: NVActor, *_):
    return actor.move("up")


def do_down(actor: NVActor, *_):
    return actor.move("down")


def do_south(actor: NVActor, *_):
    return actor.move("south")


def do_look(actor: NVActor, *_):
    actor.location.render(longp=True)
    return True


def do_inspect(actor: NVActor, target: any, _):
    here = actor.location
    target_itm = actor.bound_world.items[target]
    if target_itm in here.items:
        target_itm.render()
        return True
    return False


def do_take(actor: NVActor, target, _):
    here = actor.location
    try:
        target_itm = actor.bound_world.items.get(target, None)
        assert(target_itm.location == here)
    except AssertionError:
        return False
    except KeyError:
        return False
    return actor.add_item(target_itm)


def do_drop(actor: NVActor, target, _):
    try:
        target_itm = actor.inventory[target]
    except KeyError:
        return False
    return actor.drop_item(target_itm)


def do_inventory(actor: NVActor, *_):
    if len(actor.inventory):
        print("\nYour Inventory:")
        for item in actor.inventory.values():
            print(item.short_render())
        return True

    return False


def do_light(actor: NVActor, target, _):
    try:
        lamp = actor.inventory[target]
        assert(isinstance(lamp, NVLamp))
    except AssertionError:
        return False
    except KeyError:
        return False

    """
    Possibilities for error handling:
    - Return True if the command succeeds, some non-Boolean value if not.

      Advantage: I could return a string describing the nature of the error,
      allowing me to call the right string within the error printing routine.

      Disadvantage: It is nonintuitive to return a truthy value if the command
      fails.  My inner C programmer cringes at the thought of a method having
      one of multiple potential return types (gross abuses of void* be damned).
    '''''''''''''''''''''
    - Return the empty string if the command succeeds, some nonempty string
      if not.

      Advantage: This is a direct subscript into the errortext dict on a verb.

      Disadvantage: Again, it is counterintuitive to return a truthy value if
      we are in an error condition and it is doubly counterintuitive to return
      a falsy value if the command succeeds!
    '''''''''''''''''''''
    - Re-raise caught exceptions and make NVVerb.invoke deal with it.
    
      Advantage: No fucking around with return types - I can still return a
      truthy value if the command succeeds.  It's elegant and arguably the most
      Pythonic solution.  I'd have to learn more about how Python exceptions
      work.

      Disadvantage: Really wants custom exception classes.  I'd have to learn
      more about how Python exceptions work.
      
      Note: I would want NVBadArgError, NVNoArgError, and NVBadTargetError at
      the minimum.
    """

    if lamp.lit_state:
        return False  # lamp is already lit
    else:
        lamp.lit_state = True
        return True


def do_extinguish(actor: NVActor, target, _):
    try:
        lamp = actor.inventory[target]
        assert(isinstance(lamp, NVLamp))
    except AssertionError:
        return False
    except KeyError:
        return False

    if not lamp.lit_state:
        return False
    else:
        lamp.lit_state = False
        return True


def do_arkhtos(*_):
    print("You have won!  Please visit https://python.org to collect your prize.\n")
    print("Spoiler: Your prize is a free download, no strings attached, of the")
    print("Python programming language, which was used to implement this game.")
    do_quit()


def do_quit(*_):
    sys.exit(0)
