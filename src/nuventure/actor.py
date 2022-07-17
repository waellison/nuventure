"""Actor module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import random
from nuventure import dbg_print, func_name, nv_print
from nuventure.item import NVItem
from nuventure.errors import NVBadArgError
from nuventure.parser import do_quit

ACTOR_TYPES = {"player", "npc"}


class NVActor:
    """
    An Actor is a character entity in the game world, such as the player
    or an NPC.  An Actor is bound to the world that it occupies and
    to the node it currently occupies within that world, as of the
    current gametic.
    """

    def __init__(
        self,
        bound_world,
        world_node,
        internal_name="PLAYER",
        friendly_name="Adventurer",
        hit_points=100,
        movement_rate=1,
    ):
        """Create a new actor object.

        Args:
            bound_world: the world object to which this actor is bound
            world_node: the node within the world where this actor is currently located
            internal_name: the internal friendly_name of this actor (defaults to "PLAYER")
            friendly_name: the friendly_name of this actor (defaults to "Adventurer")
            hit_points: the amount of hit points to give this character (defaults to 100)
            movement_rate: the actor's movement rate (defaults to 1 node per gametic)
        """
        self.internal_name = internal_name
        self.friendly_name = friendly_name
        self.bound_world = bound_world
        self.location = world_node
        self.hit_points = hit_points
        self.inventory = {}
        self.description = None

        if self.is_npc():
            self.bound_world.actors[self.internal_name] = self

        self.movement_rate = movement_rate

    def __str__(self):
        """Returns the actor's friendly_name."""
        return self.friendly_name

    def injure(self, amount: int = 5) -> bool:
        """Injures an actor, detracting the specified amount of HP.

        Arguments:
            amount: the amount by which to reduce the actor's
                health (defaults to 5)

        Returns True if the actor is dead, False otherwise."""
        self.hit_points -= amount
        return self.is_dead()

    def is_dead(self) -> bool:
        """Returns whether the actor is dead."""
        return self.hit_points <= 0

    def is_npc(self) -> bool:
        """Returns whether the actor is a player character."""
        return self.internal_name != "PLAYER"

    def do_tic(self) -> None:
        """Do this actor's tic during the world tic."""
        dbg_print(func_name(), f"doing tic for {self}")
        if self.is_dead():
            if self.is_npc():
                dbg_print(func_name(), f"{self} has died, removing from map")
                del self.bound_world.actors[self.internal_name]
            else:
                nv_print("You have died.")
                do_quit(None)
        else:
            if self.is_npc():
                for _ in range(0, self.movement_rate):
                    directions = list(self.location.neighbors.keys())
                    this_way = random.choice(directions)
                    movement = self.bound_world.game_instance.parser.verbs[this_way]
                    movement.invoker = self
                    movement.target = this_way
                    movement.invoke()

    def move(self, direction) -> bool:
        """Attempts to move the actor within the world map.

        Args:
            direction: The direction in which to attempt to move the character.

        Returns:
            True if movement succeeded, False if not, None if the movement verb
            was invalid."""
        last_location = self.location
        movement_succeeded_p = self.bound_world.try_move(self, direction)

        if not movement_succeeded_p:
            raise NVBadArgError(direction, direction)

        if movement_succeeded_p and not self.is_npc():
            nv_print(last_location.neighbors[direction]["travel_description"])
            self.location.render()
        return movement_succeeded_p

    def add_item(self, item: NVItem) -> bool:
        """Add an item to the player's inventory.

        Args:
            item: the item to add to the inventory

        Returns:
            True if successful, False otherwise"""
        if item:
            item.take(self)
            self.inventory[item.internal_name] = item
            return True

        return False

    def drop_item(self, item: NVItem) -> bool:
        """Remove an item from the player's inventory and drop it at the
        current map node.

        Args:
            item: the item to drop

        Returns:
            True if successful, False otherwise"""
        if item and self.inventory.get(item.internal_name):
            item.drop(self)
            nv_print(
                f"You remove the {item.friendly_name} from your pack and set it aside."
            )
            del self.inventory[item.internal_name]
            return True
        return False
