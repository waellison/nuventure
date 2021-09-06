import sys
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
    target_itm = actor.bound_world.items.get(target, None)
    if target_itm in here.items:
        return actor.add_item(target_itm)
    return False


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


def do_arkhtos(*_):
    print("You have won!  Please visit https://python.org to collect your prize.\n")
    print("Spoiler: Your prize is a free download, no strings attached, of the")
    print("Python programming language, which was used to implement this game.")
    do_quit()


def do_quit(*_):
    sys.exit(0)
