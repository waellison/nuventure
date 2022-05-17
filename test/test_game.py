from nuventure import game, world

game_fixture = game.NVGame("./data")


def test_create_game():
    assert game_fixture.start_node.internal_name == "ORIGIN"
    assert not game_fixture.player.is_npc()
    assert game_fixture.player in game_fixture.world.actors.values()
