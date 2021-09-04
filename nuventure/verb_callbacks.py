import sys
import textwrap
from nuventure.actor import NVActor


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


def do_inspect(actor: NVActor, target: any, _):
    here = actor.location
    target_itm = actor.bound_world.items[target]
    if target_itm in here.items:
        target_itm.render()


def do_take(actor: NVActor, target, _):
    here = actor.location
    target_itm = actor.bound_world.items[target]
    if target_itm in here.items:
        target_itm.take(actor)


def do_drop(actor: NVActor, target, _):
    try:
        target_itm = actor.inventory[target]
    except KeyError:
        print(f"{target} not in inventory")
        return
    target_itm.drop(actor)


def do_inventory(actor: NVActor, *_):
    print("\nYour Inventory:")
    for item in actor.inventory.values():
        print(item.short_render())


def do_quit(*_):
    sys.exit(0)
