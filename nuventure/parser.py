"""Parser module for Nuventure, a poor man's implementation of ScummVM.

NVParser requires the NLTK library for parsing input text.  It is also in
dire need of proper documentation.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

from typing import Callable
from nuventure.actor import NVActor
from nltk import ne_chunk, pos_tag, word_tokenize
import json
from nuventure.verb_callbacks import *

VERB_PREFIX = "do_"

SIMPLE_ACTIONS = {
    "inventory", "look", "east", "north", "south",
    "west", "up", "down", "quit", "dig", "help",
    "iddqd", "xyzzy", "idkfa", "arkhtos"
}

TARGET_ACTIONS_NO_IMPL = {
    "inspect", "cast", "open", "close", "read",
    "speak", "take", "steal", "drop"
}

TARGET_ACTIONS_IMPL_FIRST = {
    "buy", "sell", "cast", "insert", "remove"
}

TARGET_ACTIONS_TARGET_FIRST = {
    "attack", "lock", "unlock"
}

ALL_VERBS = SIMPLE_ACTIONS | TARGET_ACTIONS_TARGET_FIRST \
    | TARGET_ACTIONS_IMPL_FIRST | TARGET_ACTIONS_NO_IMPL


class NVVerb:
    """
    """

    def __init__(self, name: str, callback: Callable[[NVActor, any, any], None],
                 helptext: str, errortext: str):
        """Creates a new verb object.

        Verbs represent permissible actions in the Nuventure engine.  A given Verb
        is bound to the actor that invokes it, the world object in which it is invoked,
        and the item and target, if needed.
        """
        self.name = name
        self.invoker = None
        self.bound_item = None
        self.target = None
        self.callback = callback
        self.helptext = helptext
        self.errortext = errortext

    def invoke(self):
        return self.callback(self.invoker, self.target, self.bound_item)

    def help(self):
        # Don't give away the cheat codes (which have no helptext obviously)
        if self.helptext:
            print(f"{self.name}\t\t{self.helptext}")

    def __str__(self):
        if self.target and self.bound_item:
            return f"{self.invoker} invokes {self.callback} on {self.target} with {self.bound_item}"
        if self.target:
            return f"{self.invoker} invokes {self.callback} on {self.target}"
        else:
            return f"{self.invoker} invokes {self.callback}"


class NVParser:
    def __init__(self, verbtable="./verbs.json"):
        self.verbs = {}
        self.last_command = ""
        with open(verbtable, "r") as fh:
            db = json.load(fh)

        for verb, rest in db.items():
            vname = VERB_PREFIX + verb
            helptext = rest["helptext"]
            errtext = rest["errortext"]

            if vname in globals():
                cbk = globals()[vname]

            if "aliases" in rest.keys():
                for alias in rest["aliases"]:
                    if alias in ALL_VERBS:
                        aname = VERB_PREFIX + alias
                        if aname in globals():
                            cbk = globals()[aname]
                            self.verbs[alias] = NVVerb(
                                alias, cbk, helptext, errtext)
                        else:
                            raise NotImplementedError(f"need to write {aname}")
                    else:
                        raise RuntimeError(
                            f"Catastrophic failure (cannot add nonexistent verb \"{alias}\"")
            else:
                self.verbs[verb] = NVVerb(verb, cbk, helptext, errtext)

    def read_command(self, actor):
        try:
            tmp = input("> ")
        except EOFError:
            do_quit()
        else:
            self.last_command = tmp

        action = self.do_parse(tmp)
        if isinstance(action, NVVerb):
            action.invoker = actor
        else:
            action = None
        return action

    def do_parse(self, input_string):
        if not input_string:
            return None

        bareword = input_string.split()[0]
        if not bareword in ALL_VERBS:
            return None

        if bareword == "help":
            return self.do_help(input_string)

        if input_string in SIMPLE_ACTIONS:
            return self.verbs[input_string]

        input_string = "I " + input_string
        return self.do_hard_parse(input_string)

    def do_help(self, in_str):
        tokens = in_str.split(" ", maxsplit=2)
        help_word = None

        if len(tokens) > 1:
            help_word = tokens[1]

        if help_word:
            try:
                self.verbs[help_word].help()
            except KeyError:
                print(f"nonexistent command \"{help_word}\"")
        else:
            for verb in self.verbs.values():
                verb.help()

    def do_hard_parse(self, input_string):
        entities = ne_chunk(pos_tag(word_tokenize(input_string)))
        target = None
        action = None
        implement = None
        noun_candidates = []

        for i in entities:
            if i[1] == "VBP":
                try:
                    action = globals()[f"do_{i[0]}"]
                except:
                    raise NotImplementedError(f"unimplemented action {i[0]}")
                verb = i[0]
            elif i[1] in {"NN", "JJ", "NNS"}:
                noun_candidates.append(i[0])

        # Validate input here to make sure that the implement and target are valid.
        if verb == "turn":
            if entities[2][0] == "on":
                action = globals()["do_lamp_activate"]
                target = "lamp"
                implement = None
            elif entities[2][0] == "off":
                action = globals()["do_lamp_deactivate"]
                target = "lamp"
                implement = None
            else:
                return self.error(verb)
        elif len(noun_candidates) == 2:
            if verb in TARGET_ACTIONS_IMPL_FIRST:
                implement = noun_candidates[0]
                target = noun_candidates[1]
            elif verb in TARGET_ACTIONS_TARGET_FIRST:
                implement = noun_candidates[1]
                target = noun_candidates[0]
            else:
                # Needs moar error checking
                return self.error(verb)
        elif len(noun_candidates) == 1:
            if verb in TARGET_ACTIONS_NO_IMPL:
                target = noun_candidates[0]
            else:
                # Needs moar error checking
                return self.error(verb)

        retval = NVVerb(verb, None, None, None)
        retval.target = target
        retval.bound_item = implement
        retval.callback = action
        return retval

    def error(self, whoopsie: str):
        verb = self.verbs.get(whoopsie, None)
        if verb:
            print(verb.errortext)
        else:
            print("Unspecified error")
