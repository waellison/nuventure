import pytest
from nuventure import game, parser, actor

game_fixture = game.NVGame("data")
test_fixture = game_fixture.parser


def test_get_callback_will_fail_with_bad_callback():
    with pytest.raises(RuntimeError) as ex:
        _ = parser._get_callback("foo", "do_foo")
        assert ex.value == "Catastrophic failure (cannot find callback for verb 'foo'; do_foo was passed)"


def test_get_callback_will_succeed_with_existent_callback():
    fxn = parser._get_callback("inventory", "do_inventory")
    assert fxn == parser.do_inventory


def test_cheat_code_has_no_helptext(capsys):
    cheat = test_fixture.verbs["xyzzy"]
    cheat.help()
    stdout = capsys.readouterr().out
    assert not stdout


def test_regular_command_has_helptext(capsys):
    command = test_fixture.verbs["inventory"]
    command.help()
    stdout = capsys.readouterr().out
    assert stdout == "inventory      View your inventory.\n"


def test_verbose_help_not_implemented():
    command = test_fixture.verbs["take"]
    with pytest.raises(NotImplementedError) as ex:
        command.help(verbose=True)
        assert ex.value == "verbose help is not yet implemented"


def test_dwim():
    candidates = parser._dwim("lgith")

    # The exact contents of the candidates array is prone to
    # changing since there are possibly multiple words with the
    # same Levenshtein distance to the input.  Because of this,
    # I am only testing the first candidate proposed, as this
    # should remain consistent.
    assert candidates[0] == "light"
    assert len(candidates) == 3


def test_parser_cmd_not_invocable_by_npc():
    an_npc = actor.NVActor(game_fixture.world, game_fixture.start_node, internal_name="SOME_GUY")
    with pytest.raises(RuntimeError) as ex:
        test_fixture.read_command(an_npc)
        assert ex.value == "Non-player characters should not invoke interactive commands"
