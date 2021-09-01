import textwrap
import sys


def verb_move(parser, actor):
    direction = parser.current_input[0]
    return actor.move(direction)


def verb_look(parser, actor):
    here = actor.location
    here.render()


def verb_help(parser, _):
    # yuck
    help_word = ""
    if len(parser.current_input) > 1:
        help_word = parser.current_input[1].split(" ")[0]

    if help_word:
        parser.verbs[help_word].help()
    else:
        for verb in parser.verbs.values():
            verb.help()


def verb_quit(*args):
    sys.exit(0)