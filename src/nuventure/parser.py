"""Parser module for Nuventure, a poor man's implementation of ScummVM.

NVParser requires the NLTK library for parsing input text.  It is also in
dire need of proper documentation.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import sys
import json
from typing import Callable, Tuple, Union

from functools import cmp_to_key
from thefuzz import fuzz
from nltk import ne_chunk, pos_tag, word_tokenize

from . import ERROR_STR, nv_print
from .errors import (
    NVBadArgError,
    NVNoArgError,
    NVBadTargetError,
    NVGameStateError,
    NVParseError,
)
from .item import NVLamp

VERB_PREFIX = "do_"

"""Terminals denoting simple actions (i.e., verbs of the fourth type, which
do not require targets)."""
SIMPLE_ACTIONS = {
    "inventory",
    "look",
    "quit",
    "dig",
    "iddqd",
    "xyzzy",
    "idkfa",
    "arkhtos",
}

"""Terminals denoting movement directions (i.e., verbs of the sixth type)"""
DIRECTIONS = {"north", "south", "east", "west", "up", "down"}

"""Terminals denoting cheat actions or victory conditions."""
CHEAT_ACTIONS = {"iddqd", "idkfa", "xyzzy", "arkhtos"}

"""Terminals denoting item-bearing actions (i.e., verbs of the third type,
which only require a target)."""
TARGET_ACTIONS_NO_IMPL = {
    "inspect",
    "cast",
    "open",
    "close",
    "read",
    "speak",
    "take",
    "steal",
    "drop",
    "light",
    "extinguish",
}

"""Terminals denoting targeted actions where the item comes first and the
target comes second (verbs of the second type)."""
TARGET_ACTIONS_IMPL_FIRST = {"buy", "sell", "cast", "insert", "remove"}

"""Terminals denoting targeted actions where the target comes first and the
item comes second (verbs of the first type)."""
TARGET_ACTIONS_TARGET_FIRST = {"attack", "lock", "unlock"}

"""The sole terminal denoting the help action, which is the only verb of the
fifth type."""
HELP_ACTION = {"help"}

"""A set of all verbs, which is a simple union of the five types of verb
terminals recognized by Nuventure."""
ALL_VERBS = (
    SIMPLE_ACTIONS
    | TARGET_ACTIONS_TARGET_FIRST
    | TARGET_ACTIONS_IMPL_FIRST
    | TARGET_ACTIONS_NO_IMPL
    | HELP_ACTION
    | DIRECTIONS
)

"""A set of the verbs which require a target."""
ALL_TARGETED_VERBS = (
    TARGET_ACTIONS_IMPL_FIRST | TARGET_ACTIONS_NO_IMPL | TARGET_ACTIONS_TARGET_FIRST
)


def _get_callback(verb: str, cbk_name: str) -> Callable:
    """
    Retrieve a callback from the global namespace.

    Returns:
        The callback function if found

    Raises:
        `RuntimeError` if the verb is not listed in `ALL_VERBS` even if
            a callback exists
    """
    if cbk_name in globals():
        cbk = globals()[cbk_name]
    else:
        raise RuntimeError(
            f"Catastrophic failure (cannot find callback for verb '{verb}'; {cbk_name} was passed)"
        )
    return cbk


class NVVerb:
    """
    NVVerb is the class for actions invoked by the parsing engine.

    Verbs represent permissible actions in the Nuventure engine.  A
    given NVVerb is bound to the actor that invokes it, the world object
    in which it is invoked, and the item and target, if needed; they are
    set to None otherwise before NVVerb.invoke is called.
    """

    def __init__(
        self,
        name: str,
        callback,
        help_text: str,
        errortext: str,
    ):
        """Creates a new verb object."""
        self.name = name
        self.invoker = None
        self.bound_item = None
        self.target = None
        self.callback = callback
        self.help_text = help_text
        self.errortext = errortext

    def invoke(self) -> Callable:
        """Invokes the verb's bound callback.  The callback is selected and
        bound by the parsing routine."""
        return self.callback(self)

    def help(self, verbose=False) -> None:
        """Prints the verb's help text, if present."""

        # Don't give away the cheat codes (which have no helptext obviously)
        if self.help_text:
            if not verbose:
                nv_print(f"{self.name:15}{self.help_text}")
            else:
                raise NotImplementedError("verbose help is not yet implemented")


def _compare_candidate_match(c1: Tuple[int, str], c2: Tuple[int, str]) -> int:
    return c1[0] - c2[0]


def _dwim(user_input: str) -> list[str]:
    """
    Ascertain potentially meant verbs from erroneous user input.

    Args:
        user_input [str]: the user's input string

    Returns:
        A list of the top three candidates matching the input string.
    """
    command_candidates = []

    # Check the match ratio between our input and each potential match.
    # Then, add that to a list of candidates as a tuple with the ratio
    # first and the potential match second.
    #
    # I believe that TheFuzz uses the Levenshtein distance for this
    # but I am not certain without checking the documentation.
    for verb in ALL_VERBS:
        if verb in CHEAT_ACTIONS:
            continue
        ratio = fuzz.ratio(user_input, verb)
        command_candidates.append((ratio, verb))

    # Reverse-sort the candidates list to get a list of the matches
    # from best to worst.
    dwim = sorted(command_candidates, key=cmp_to_key(_compare_candidate_match), reverse=True)
    candidates = [candidate[1] for candidate in dwim[:3]]

    # Now print just the top three such matches.
    nv_print(f'I don\'t understand "{user_input}"; did you mean:')

    for candidate in candidates:
        print(f"    {candidate}")

    return candidates


class NVParser:
    """
    NVParser is responsible for handling input from the user and converting
    it into actions within the Nuventure engine.  NVParser works on verbs
    described in verbs.json in the working directory of the Nuventure
    game runner script.
    """

    def __init__(self, verb_table: str = "../data/verbs.json"):
        """Create a new parser object and load the verbs from memory."""
        self.verbs = {}
        self.last_command = ""
        with open(verb_table, "r") as fh:
            db = json.load(fh)

        for verb, rest in db.items():
            # special case: `help` is handled elsewhere
            if verb == "help":
                continue

            help_text = rest["helptext"]
            error_text = rest["errortext"]

            callback = _get_callback(verb, rest["callback"])

            if "aliases" in rest.keys():
                for alias in rest["aliases"]:
                    self.verbs[alias] = NVVerb(alias, callback, help_text, error_text)
            else:
                self.verbs[verb] = NVVerb(verb, callback, help_text, error_text)

    def read_command(self, actor) -> NVVerb:
        """Read a command from an actor.  The actor must be the player
        character.  If not, this command will raise an exception.

        Args:
            actor: the actor on whose behalf we are executing a command
                (must be an NVActor instance)

        Returns: The NVVerb object corresponding to the entered command if
            the parse was successful, None otherwise.

        Raises:
            RuntimeError: if an NPC is passed as the invoking actor
        """
        tmp = ""

        if actor.internal_name != "PLAYER":
            raise RuntimeError(
                "Non-player characters should not invoke interactive commands"
            )

        try:
            tmp = input("> ")
        except (EOFError, KeyboardInterrupt):
            do_quit()
        else:
            self.last_command = tmp

        action = self.do_parse(tmp)
        if action is NVVerb:
            action.invoker = actor
        else:
            action = None

        return action

    def do_parse(self, input_string: str) -> Union[NVVerb, None]:
        """
        Execute the actual parsing of the command string.  This method
        checks for some simple edge cases before invoking the real parsing
        method if needed.

        Args:
            input_string: the input read by NVParser.read_command

        Returns:
            An NVVerb object describing the parsed command; None if the
            command is not found or is invalid.
        """
        if not input_string:
            return None

        # Verify that the user's input even contains a valid verb before
        # proceeding.  Use fuzzy matching to propose potential matches if
        # an invalid input is given, but just return None if there is no
        # input at all.
        input_string = input_string.lower()
        tokens = input_string.split()
        if not tokens:
            return None
        elif not tokens[0] in ALL_VERBS:
            _dwim(tokens[0])
            raise NVParseError(tokens[0])

        # The "help" bareword is a special case since it does not need to
        # invoke a callback.  The "help" bareword is the "fifth type" of
        # verb in Nuventure.
        if tokens[0] == "help":
            return self.do_help(input_string)

        # Simple actions require no arguments.  These are considered to be
        # the "fourth type" of verbs in Nuventure.  The compass directions
        # are a special case of this, since they all invoke the "move" method,
        # with the name of the direction as its "target;" because of this
        # special handling, they are the "sixth type" of verbs in Nuventure.
        if input_string in SIMPLE_ACTIONS:
            return self.verbs[input_string]
        elif input_string in DIRECTIONS:
            verb = self.verbs[tokens[0]]
            verb.target = tokens[0]
            return verb

        # Make it a (mostly) valid English sentence and then hand it over to
        # the real parser.
        input_string = "I " + input_string
        return self.do_hard_parse(input_string)

    def do_help(self, input_string: str) -> None:
        """
        Implements the `help` command.  Shows help for a specific verb
        if called with that verb, else shows a summary of all commands.

        Args:
            input_string: the input string to show the help string for.

        Returns:
            Nothing
        """
        tokens = input_string.split(" ", maxsplit=2)
        help_word = None

        if len(tokens) > 1:
            help_word = tokens[1]

        if help_word:
            try:
                self.verbs[help_word].help()
            except KeyError:
                nv_print(f'nonexistent command "{help_word}"')
        else:
            for verb in self.verbs.values():
                verb.help()

    def do_hard_parse(self, input_string: str) -> Union[NVVerb, None]:
        """
        Invokes the "real" parsing routine for more complex commands.
        This uses NLTK to create a parse tree from the user's input.

        Args:
            input_string: The user's input string as typed.

        Returns:
            The `NVVerb` object corresponding to the player's input if
            it exists and the input is valid, None otherwise.
        """
        verb = None
        target = None
        implement = None
        noun_candidates = []

        # Break the input string into tagged entities, which we will use
        # to extract the relevant parts.
        entities = ne_chunk(pos_tag(word_tokenize(input_string)))

        # Each entity in the input sentence is tagged by what it is.
        # These are just tuples contained within a list.
        #
        # Verbs are the heads of verb phrases, hence they are marked
        # by VBP.  We will later attempt to retrieve the relevant verb
        # from the parser's verb table, but for now it suffices just
        # to pick it from the input text.
        #
        # There are potentially multiple nouns in an input sentence,
        # and we select them from the entity list by looking at the
        # tag which they have been given: NN, JJ, or NNS.
        #
        # Note for future reference:
        # Proper names of people are handled differently and are
        # tagged with the tuple `(PERSON, PersonName/NNP)`; as such,
        # they need special handling when the speak, steal, buy, and
        # and sell actions are implemented.
        for i in entities:
            if i[1] in {"VBP", "VBD"}:
                verb = i[0]
            elif i[1] in {"NN", "JJ", "NNS"}:
                noun_candidates.append(i[0])

        # There are two types of commands that accept two arguments:
        # those that accept the target first (the "first type"), and
        # those that accept the "implement" (an item or spell) first
        # (the "second type").  Here we determine which applies.
        #
        # In linguistic terms this is the position of the direct and
        # indirect (if present) objects within the input sentence, and
        # which word is which.
        #
        # If there is only one argument to a given verb, then we assume
        # it to be the target.  This is the third type of verb in the
        # Nuventure engine.  Verbs of the fourth, fifth, and sixth types
        # are handled in NVParser.do_parse, as they do not require NLTK
        # to aid in parsing.
        #
        # An example of the first type is "unlock the door with the key".
        # An example of the second type is "cast fire on the goblin".
        # An example of the third type is "extinguish the lamp".
        #
        # If parsing the argument list fails, error and return None.
        # There are three possible error states: if an argument is
        # required but none is supplied (or too many are supplied);
        # if one argument is given but two are required; and if too
        # many arguments are given to a verb that only requires one.
        if len(noun_candidates) == 2:
            if verb in TARGET_ACTIONS_IMPL_FIRST:
                implement = noun_candidates[0]
                target = noun_candidates[1]
            elif verb in TARGET_ACTIONS_TARGET_FIRST:
                implement = noun_candidates[1]
                target = noun_candidates[0]
            else:
                self.error(verb)
                return None
        elif len(noun_candidates) == 1:
            if verb in TARGET_ACTIONS_NO_IMPL:
                target = noun_candidates[0]
            else:
                self.error(verb)
                return None
        else:
            if verb in ALL_TARGETED_VERBS:
                self.error(verb)
                return None

        # Once the type of verb and arguments have been determined,
        # pull the appropriate verb and set its target and bound item
        # appropriately, then return it to the caller for invocation.
        retval = self.verbs[verb]
        retval.target = target
        retval.bound_item = implement
        return retval

    def error(self, whoopsie: str) -> None:
        """
        Print an error message if parsing generates an error.
        """
        verb = self.verbs.get(whoopsie, None)
        if verb:
            nv_print(verb.errortext)
        else:
            nv_print(ERROR_STR)

    def rich_error(self, whoopsie: str, which: str, target: Union[any, None] = None) -> None:
        """
        Print a nicer error message if parsing generates an error.
        """
        verb = self.verbs.get(whoopsie, None)
        if verb:
            if target:
                estring = verb.errortext.get(which, ERROR_STR + " (target was: {0})")
                output = estring.format(target)
            else:
                output = verb.errortext.get(which, ERROR_STR)
            nv_print(output)
        else:
            nv_print(ERROR_STR)


def do_move(verb: NVVerb) -> bool:
    """Attempt to move the given character in the specified direction."""
    try:
        return verb.invoker.move(verb.target)
    except NVBadArgError as ex:
        raise NVBadArgError("move", verb.target) from ex


def do_look(verb: NVVerb) -> bool:
    """Print a description of the cell where the player is."""
    print_state = False
    if verb.invoker.location.wanted_state == "lamp_lit":
        lamp = verb.invoker.inventory.get("lamp")
        if lamp is NVLamp and lamp.is_lit():
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


def do_take(verb: NVVerb) -> bool:
    """
    Take an item from the scene and put it in the player's inventory,
    if it exists in the same cell as the player.
    """
    here = verb.invoker.location
    try:
        target_itm = verb.invoker.bound_world.items.get(verb.target, None)
        assert target_itm.location == here
    except (AssertionError, AttributeError) as ex:
        raise NVBadArgError("take", verb.target) from ex
    except KeyError as ex:
        raise NVBadTargetError("take", verb.target) from ex
    else:
        return verb.invoker.add_item(target_itm)


def do_drop(verb: NVVerb) -> bool:
    """
    Take an item from the player's inventory and place it in the cell
    where the player is.
    """
    try:
        target_itm = verb.invoker.inventory[verb.target]
    except KeyError as ex:
        raise NVBadArgError("drop", verb.target) from ex
    else:
        return verb.invoker.drop_item(target_itm)


def do_inventory(verb: NVVerb) -> bool:
    """
    Show the player's inventory, if there is anything in it.
    """
    if verb.invoker.inventory:
        nv_print("\nYour Inventory:")
        for item in verb.invoker.inventory.values():
            nv_print(item.short_render())
        return True

    raise NVNoArgError("inventory")


def do_light(verb: NVVerb) -> bool:
    """
    Light the player's lamp, if the player has it and it is not lit.
    """
    try:
        lamp = verb.invoker.inventory[verb.target]
        assert lamp is NVLamp
    except AssertionError as ex:
        raise NVBadArgError("light", verb.target) from ex
    except KeyError as ex:
        raise NVBadTargetError("light", verb.target) from ex

    if lamp.is_lit():
        raise NVGameStateError("light")

    lamp.use()
    return True


def do_extinguish(verb: NVVerb) -> bool:
    """
    Extinguish the player's lamp, if the player has it, and if it is lit.
    """
    try:
        lamp = verb.invoker.inventory[verb.target]
        assert lamp is NVLamp
    except AssertionError as ex:
        raise NVBadArgError("extinguish", verb.target) from ex
    except KeyError as ex:
        raise NVBadTargetError("extinguish", verb.target) from ex

    if not lamp.is_lit():
        raise NVGameStateError("extinguish")

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
        do_quit(verb)
    else:
        raise NVGameStateError("arkhtos")


def do_xyzzy(_: NVVerb) -> None:
    """Trigger the game's loss condition."""
    nv_print(
        """Your memory serves you well.

However, you choose poorly.  Goodbye.
\n
\nYou have died.
"""
    )
    do_quit(_)


def do_quit(_: NVVerb) -> None:
    """Quit the game."""
    sys.exit(0)
