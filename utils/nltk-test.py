"""Testing the functionality of NLTK, the Natural Langauge ToolKit.

NLTK provides an easy way to work with natural language input."""

from nltk import ne_chunk, pos_tag, word_tokenize
import sys

directions = {"east", "north", "south", "west", "up", "down"}

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
    "steal"
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


class Verb:
    def __init__(self, source, dest, byword, cbk):
        self.source = source
        self.dest = dest
        self.byword = byword
        self.cbk = cbk

    def __str__(self):
        if self.dest and self.byword:
            return f"{self.source} invokes {self.cbk} on {self.dest} with {self.byword}"
        if self.dest:
            return f"{self.source} invokes {self.cbk} on {self.dest}"
        else:
            return f"{self.source} invokes {self.cbk}"


def do_parse(input_string):
    if input_string in simple_actions:
        print("SIMPLE COMMAND: " + input_string)
        return Verb("player", None, None, "do_" + input_string)

    input_string = "I " + input_string

    return do_hard_parse(input_string)


def do_hard_parse(input_string):
    entities = ne_chunk(pos_tag(word_tokenize(input_string)))
    target = None
    action = None
    implement = None
    noun_candidates = []

    for i in entities:
        if i[1] == "VBP":
            action = f"do_{i[0]}"
            verb = i[0]
        elif i[1] == "NN" or i[1] == "JJ":
            noun_candidates.append(i[0])

    # Validate input here to make sure that the implement and target are valid.
    if len(noun_candidates) == 2:
        if verb in target_actions_impl_first:
            implement = noun_candidates[0]
            target = noun_candidates[1]
        elif verb in target_actions_target_first:
            implement = noun_candidates[1]
            target = noun_candidates[0]
        else:
            # Needs moar error checking
            return error(verb)
    elif len(noun_candidates) == 1:
        if verb in target_actions_no_impl:
            target = noun_candidates[0]
        else:
            # Needs moar error checking
            return error(verb)

    return Verb("player", target, implement, action)


def error(whoopsie):
    errors = {
        "attack": "With what, your bare hands?",
        "unlock": "With what, a bobby pin?"
    }
    return errors.get(whoopsie, "Unspecified parse error")


def input_loop():
    while True:
        try:
            in_str = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("")
            sys.exit(0)

        if not in_str:
            continue

        if in_str == "EXIT!":
            sys.exit(0)

        verb = do_parse(in_str)
        if verb:
            print(verb)
        else:
            print("Parse error")


print("Try me!  Type 'EXIT!' to exit.")
input_loop()
