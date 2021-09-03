from nuventure.item import Item
from nuventure.world import World
from nuventure.actor import Actor
import textwrap
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
    if target in here.items:
        target.take(actor)


"""
def do_help(parser, _):
    help_word = ""
    if len(parser.current_input) > 1:
        help_word = parser.current_input[1].split(" ")[0]

    if help_word:
        parser.verbs[help_word].help()
    else:
        for verb in parser.verbs.values():
            verb.help()
"""


def do_quit(*_):
    sys.exit(0)
