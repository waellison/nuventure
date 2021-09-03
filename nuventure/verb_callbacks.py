from nuventure.actor import Actor
import sys


def do_east(actor: Actor, *_):
    return actor.move("east")


def do_west(actor: Actor, *_):
    return actor.move("west")


def do_north(actor: Actor, *_):
    return actor.move("north")


def do_up(actor: Actor, *_):
    return actor.move("up")


def do_down(actor: Actor, *_):
    return actor.move("down")


def do_south(actor: Actor, *_):
    return actor.move("south")


def do_look(actor: Actor, *_):
    actor.location.render()


def do_take(actor: Actor, target, _):
    here = actor.location
    target_itm = actor.bound_world.items[target]
    if target_itm in here.items:
        target_itm.take(actor)


def do_drop(actor: Actor, target, _):
    try:
        target_itm = actor.inventory[target]
    except KeyError:
        print(Parser.error("drop"))
        return
    target_itm.drop(actor)


def do_inventory(actor: Actor, *_):
    print("\nYour Inventory:")
    for item in actor.inventory.values():
        print(item.short_render())


def do_quit(*_):
    sys.exit(0)
