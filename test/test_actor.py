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
                  iname="SIDEKICK",
                  name="Alandar",
                  hp=50,
                  movement_rate=1
                )

item_fixture = NVLamp(
    iname="Test Lamp",
    dbinfo={
        "friendlyName": "Test Lamp",
        "inSceneDescription": "It's a lamp.",
        "longDescription": "It's a lamp.",
        "takeDescription": "You pick the lamp up.",
        "useDescription": "You turn the lamp on.",
        "useAltDescription": "You turn the lamp off.",
        "originCell": "ORIGIN",
        "originOwner": None
    },
    world=game_fixture.world
)


def test_actor_stringize():
    assert str(actor_fixture) == "Alandar"


def test_injure_actor():
    test_dummy = NVActor(None, None, hp=100)
    test_dummy.injure(10)
    assert test_dummy.hit_points == 90


def test_kill_actor():
    test_dummy = NVActor(None, None)
    test_dummy.injure(100)
    assert test_dummy.is_dead()


def test_npc_detect():
    assert actor_fixture.is_npc()


def test_player_detect():
    test_player = NVActor(None, None)
    assert not test_player.is_npc()


def test_player_move_ok():
    result = actor_fixture.move("up")
    assert result


def test_player_move_fail():
    with pytest.raises(NVBadArgError) as ex:
        result = actor_fixture.move("north")


def test_item_bestowal():
    result = actor_fixture.add_item(item_fixture)
    assert result


def test_item_removal():
    result = actor_fixture.drop_item(item_fixture)
    assert result
