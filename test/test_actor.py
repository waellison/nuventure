from nuventure.actor import NVActor
from nuventure.item import NVItem

actor_fixture = NVActor(
                  None,
                  None,
                  iname="SIDEKICK",
                  name="Alandar",
                  hp=50,
                  movement_rate=1
                )

def test_actor_stringize():
  global actor_fixture
  assert str(actor_fixture) == "Alandar"

