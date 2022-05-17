from nuventure import errors


def test_NVParseError():
    error = errors.NVParseError(verb="test")
    assert error.what == "test"


def test_NVTargetError():
    error = errors.NVBadTargetError(verb="attack", arg="orc")
    assert error.verb == "attack"
    assert error.arg == "orc"
    assert error.et_key == "badtgt"


def test_NVBadArgError():
    error = errors.NVBadArgError(verb="attack", arg="orc")
    assert error.verb == "attack"
    assert error.arg == "orc"
    assert error.et_key == "badarg"


def test_NVNoArgError():
    error = errors.NVNoArgError(verb="attack")
    assert error.verb == "attack"
    assert error.et_key == "noargs"


def test_NVGameStateError():
    error = errors.NVGameStateError(verb="what")
    assert error.verb == "what"
