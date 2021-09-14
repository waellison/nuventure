"""Actor module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import textwrap
from nuventure import dbg_print, func_name
from nuventure.world import NVWorld, NVWorldNode
from nuventure.item import NVItem
from nuventure.errors import NVBadArgError

ACTOR_TYPES = {"player", "npc"}


class NVActor:
    """
    An Actor is a character entity in the game world, such as the player
    or an NPC.  An Actor is bound to the world that it occupies and
    to the node it currently occupies within that world, as of the
    current gametic.
    """

    def __init__(self, bound_world: NVWorld, location: NVWorldNode, name="Adventurer", hp=100, actor_type="player", movement_rate=1):
        """Create a new actor object.

        Args:
            bound_world: the world object to which this actor is bound
            location: the node within the world where this actor is currently located
            name: the name of this actor (defaults to "Adventurer")
            hp: the amount of hit points to give this character (defaults to 100)
            actor_type: the type of actor this is (player or NPC)
            movement_rate: the actor's movement rate (defaults to 1 node per gametic)
        """
        self.name = name
        self.bound_world = bound_world
        self.location = location
        self.hit_points = hp
        self.inventory = {}

        if actor_type in ACTOR_TYPES:
            self.actor_type = actor_type
        else:
            raise KeyError(f"invalid actor type for actor {self.name}")

        self.movement_rate = movement_rate

    def __str__(self):
        """Returns the actor's name."""
        return self.name

    def injure(self, amount=5):
        """Injures an actor, detracting the specified amount of HP.

        Arguments:
            amount: the amount by which to reduce the actor's
                health (defaults to 5)

        Returns True if the actor is dead, False otherwise."""
        self.hit_points -= amount
        return self.is_dead()

    def is_dead(self):
        """Returns whether the character is dead."""
        return self.hit_points == 0

    def move(self, direction):
        """Attempts to move the actor within the world map.

        Args:
            direction: The direction in which to attempt to move the character.

        Returns:
            True if movement succeeded, False if not, None if the movement verb
            was invalid."""
        prev_loc = self.location
        result = self.bound_world.try_move(self, direction)

        if not result:
            raise NVBadArgError(direction, direction)

        if result and self.actor_type == "player":
            print(*textwrap.wrap(prev_loc.neighbors[direction]["travel_description"],
                                 width=72), sep="\n")
            print("")
            self.location.render()
        return result

    def add_item(self, item: NVItem):
        """Add an item to the player's inventory.

        Args:
            item: the item to add to the inventory"""
        if item:
            dbg_print(
                func_name(), f"taking item {item.internal_name} for owner {self}")
            item.take(self)
            self.inventory[item.internal_name] = item
            return True

        return False

    def drop_item(self, item: NVItem):
        """Remove an item from the player's inventory and drop it at the
        current map node.

        Args:
            item: the item to drop"""
        if self.inventory.get(item.internal_name):
            dbg_print(
                func_name(), f"dropping item {item.internal_name} from owner {self}")
            item.drop(self)
            print(
                f"You remove the {item.friendly_name} from your pack and set it aside.")
            del self.inventory[item.internal_name]
            return True

        return False
