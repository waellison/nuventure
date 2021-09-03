from typing import Callable
from nuventure.actor import Actor
from nltk import ne_chunk, pos_tag, word_tokenize
import json
from nuventure.verb_callbacks import do_quit

_verb_prefix = "do_"

simple_actions = {
    "inventory",
    "look",
    "east",
    "north",
    "south",
    "west",
    "up",
    "down",
    "quit",
    "dig",
    "help",
    "iddqd",
    "xyzzy",
    "idkfa",
    "arkhtos"
}

target_actions_no_impl = {
    "examine",
    "cast",
    "open",
    "close",
    "read",
    "speak",
    "take",
    "steal",
    "drop"
}

target_actions_impl_first = {
    "buy",
    "sell",
    "cast",
    "insert",
    "remove"
}

target_actions_target_first = {
    "attack",
    "lock",
    "unlock"
}

all_verbs = simple_actions | target_actions_target_first \
    | target_actions_impl_first | target_actions_no_impl


class Verb:
    def __init__(self, name: str, callback: Callable[[Actor, any, any], None],
                 helptext: str, errortext: str, source=None, implement=None,
                 targetActor=None):
        """Creates a new verb object.

        Verbs represent permissible actions in the Nuventure engine.  A given Verb
        is bound to the actor that invokes it, the world object in which it is invoked,
        and the item and target, if needed.
        """
        self.name = name
        self.invoker = source
        self.bound_item = implement
        self.target = targetActor
        self.callback = callback
        self.helptext = helptext
        self.errortext = errortext

    def invoke(self):
        return self.callback(self.invoker, self.target, self.bound_item)

    def help(self):
        print(f"{self.name}\t\t{self.helptext}")

    def __str__(self):
        if self.target and self.bound_item:
            return f"{self.invoker} invokes {self.callback} on {self.target} with {self.bound_item}"
        if self.target:
            return f"{self.invoker} invokes {self.callback} on {self.target}"
        else:
            return f"{self.invoker} invokes {self.callback}"


class Parser:
    def __init__(self, verbtable="./verbs.json"):
        self.verbs = {}
        with open(verbtable, "r") as fh:
            db = json.load(fh)

        for verb, rest in db.items():
            vname = _verb_prefix + verb
            helptext = rest["helptext"]
            errtext = rest["errortext"]

            if vname in globals():
                cbk = globals()[vname]

            if "aliases" in rest.keys():
                for alias in rest["aliases"]:
                    if alias in all_verbs:
                        aname = _verb_prefix + alias
                        if aname in globals():
                            cbk = globals()[aname]
                            self.verbs[alias] = Verb(
                                alias, cbk, helptext, errtext)
                        else:
                            raise NotImplementedError(f"need to write {aname}")
                    else:
                        raise RuntimeError(
                            f"Catastrophic failure (cannot add nonexistent verb \"{alias}\"")
            else:
                self.verbs[verb] = Verb(verb, cbk, helptext, errtext)

    def read_command(self, actor):
        try:
            tmp = input("> ")
        except EOFError:
            do_quit()

        action = self.do_parse(tmp)
        if isinstance(action, Verb):
            action.invoker = actor
        else:
            action = None
        return action

    def do_parse(self, input_string):
        if input_string in simple_actions:
            return self.verbs[input_string]

        input_string = "I " + input_string
        return self.do_hard_parse(input_string)

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
            elif i[1] == "NN" or i[1] == "JJ":
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
            if verb in target_actions_impl_first:
                implement = noun_candidates[0]
                target = noun_candidates[1]
            elif verb in target_actions_target_first:
                implement = noun_candidates[1]
                target = noun_candidates[0]
            else:
                # Needs moar error checking
                return self.error(verb)
        elif len(noun_candidates) == 1:
            if verb in target_actions_no_impl:
                target = noun_candidates[0]
            else:
                # Needs moar error checking
                return self.error(verb)

        retval = Verb(verb, None, None, None)
        retval.target = target
        retval.bound_item = implement
        retval.callback = action
        return retval

    def error(self, whoopsie: str):
        if self.verbs[whoopsie].errortext:
            return self.verbs[whoopsie].errortext
        else:
            return "Unspecified error"
