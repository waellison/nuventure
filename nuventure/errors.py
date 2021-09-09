"""

"""


class NVParseError(Exception):
    def __init__(self, verb):
        self.what = verb


class NVBadTargetError(Exception):
    def __init__(self, verb, arg):
        self.verb = verb
        self.arg = arg
        self.et_key = "badtgt"


class NVBadArgError(Exception):
    def __init__(self, verb, arg):
        self.verb = verb
        self.arg = arg
        self.et_key = "badarg"


class NVNoArgError(Exception):
    def __init__(self, verb):
        self.verb = verb
        self.et_key = "noargs"


class NVGameStateError(Exception):
    def __init__(self, verb, what):
        self.verb = verb
        self.what = what
