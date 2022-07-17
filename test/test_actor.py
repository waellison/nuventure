import pytest
from pathlib import Path
from nuventure.actor import NVActor
from nuventure.item import NVItem, NVLamp
from nuventure.game import NVGame
from nuventure.errors import NVBadArgError

game_fixture = NVGame("data")

actor_fixture = NVActor(
    game_fixture.world,
    game_fixture.start_node,
    internal_name="SIDEKICK",
    friendly_name="Alandar",
    hit_points=50,
    movement_rate=1,
)

item_fixture = NVLamp(
    internal_name="Test Lamp",
    database_info={
        "friendlyName": "Test Lamp",
        "inSceneDescription": "It's a lamp.",
        "longDescription": "It's a lamp.",
        "takeDescription": "You pick the lamp up.",
        "useDescription": "You turn the lamp on.",
        "useAltDescription": "You turn the lamp off.",
        "originCell": "ORIGIN",
        "originOwner": None,
    },
    world=game_fixture.world,
)


def test_actor_stringize():
    assert str(actor_fixture) == "Alandar"


def test_injure_actor():
    test_dummy = NVActor(None, None, hit_points=100)
    test_dummy.injure(10)
    assert test_dummy.hit_points == 90


def test_kill_actor():
    test_dummy = NVActor(None, None)
    test_dummy.injure(100)
    assert test_dummy.is_dead()


def test_npc_detect():
    assert actor_fixture.is_npc()


def test_player_detect():
    actor_fixture.internal_name = "PLAYER"
    assert not actor_fixture.is_npc()


def test_player_move_ok(capsys):
    result = actor_fixture.move("up")
    captured = capsys.readouterr()
    assert captured.out == """You shimmy up the ladder to your attic.

Attic
You look around the attic of your house.  There isn't much left here,
just a few empty crates that used to store fabric and food.  The air is
musty and warm, and you start to sweat.

There is a sword lying here in its scabbard.
"""
    assert result


def test_player_move_fail():
    with pytest.raises(NVBadArgError) as ex:
        result = actor_fixture.move("north")


def test_item_bestowal():
    result = actor_fixture.add_item(item_fixture)
    assert result


def test_item_bestowal_bad_item_fails():
    result = actor_fixture.add_item(None)
    assert result is False


def test_item_removal():
    result = actor_fixture.drop_item(item_fixture)
    assert result


def test_item_removal_bad_item_fails():
    result = actor_fixture.drop_item(None)
    assert result is False


def test_actor_tic_player_died(capsys):
    test_actor = NVActor(None, None)
    test_actor.injure(100)

    with pytest.raises(SystemExit) as exit_exc:
      test_actor.do_tic()
      captured = capsys.readouterr()
      assert captured.out == "You have died."
    
    assert exit_exc.type == SystemExit


def test_actor_tic_npc_died():
    test_actor = NVActor(game_fixture.world, game_fixture.start_node, internal_name="TEST")
    test_actor.injure(100)
    test_actor.do_tic()
    assert test_actor not in game_fixture.world.actors.values()


def test_actor_tic_npc_moved():
    start_node = actor_fixture.location.internal_name
    actor_fixture.movement_rate = 1
    actor_fixture.internal_name = "SIDEKICK"
    actor_fixture.do_tic()
    assert start_node != actor_fixture.location.internal_name

