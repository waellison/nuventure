"""
Exception classes for Nuventure.

Copyright (c) 2021 William Ellison
<waellison@gmail.com>

This software is licensed under the MIT License.
"""


class NVParseError(Exception):
    """
    General parsing exception.  This is a generic error only suited for
    when there is no better exception to throw.
    """

    def __init__(self, verb):
        super().__init__()
        self.what = verb


class NVBadTargetError(Exception):
    """
    Exception to be raised when a bad target is passed to a verb.
    This should really only be used on verbs of the first or second
    type, which require two arguments.
    """

    def __init__(self, verb, arg):
        super().__init__()
        self.verb = verb
        self.arg = arg
        self.et_key = "badtgt"


class NVBadArgError(Exception):
    """
    Exception to be raised when a bad argument is passed to a verb.
    This is validly used with verbs of the first, second, or third
    types, as well as with the fifth-type verb HELP.
    """

    def __init__(self, verb, arg):
        super().__init__()
        self.verb = verb
        self.arg = arg
        self.et_key = "badarg"


class NVNoArgError(Exception):
    """
    Exception to be raised when a verb that requires one or more
    arguments is passed without any arguments.  Suitable for
    verbs of the first, second, and third types.
    """

    def __init__(self, verb):
        super().__init__()
        self.verb = verb
        self.et_key = "noargs"


class NVGameStateError(Exception):
    """
    Exception to be raised when a verb that changes game state
    encounters an invalid state.
    """

    def __init__(self, verb):
        super().__init__()
        self.verb = verb
