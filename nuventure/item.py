"""Item module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import textwrap


class NVItem:
    """
    Items are static entities in the world that enable the player to
    perform various actions, such as illuminating the active node,
    attacking enemies, or unlocking doors.
    """

    def __init__(self, iname: str, dbinfo: dict, world):
        """Create a new item.

        Args:
            iname: internal name of the item
            dbinfo: dict of data from the world JSON
            world: the world to which this item is bound"""
        self.internal_name = iname
        self.friendly_name = dbinfo["friendlyName"]
        self.look_description = dbinfo["inSceneDescription"]
        self.long_description = dbinfo["longDescription"]
        self.take_description = dbinfo["takeDescription"] or None
        self.map_node = world.nodes[dbinfo["originCell"]]
        self.owner = None
        self.map_node.add_item(self)

    def take(self, taker):
        """Take an item from the world and give it to the actor
        taking it.

        Args:
            taker: the actor taking the item

        Returns:
            Nothing.

        See Also:
            NVActor.take_item"""
        if not self.take_description:
            print(f"You cannot take the {self.friendly_name}.")
        else:
            print(self.take_description)
            self.owner = taker
            self.map_node.items.remove(self)
            self.map_node = None

    def drop(self, giver):
        """Drop an item back into the world, taking it from the
        actor giving it back to the item.

        Args:
            giver: the actor dropping the item

        Returns:
            Nothing.

        See Also:
            NVActor.drop_item"""
        self.owner = None
        self.map_node = giver.location
        self.map_node.items.append(self)

    def __str__(self):
        return self.internal_name

    def _describe(self):
        """
        Show the description of the item.
        """
        return self.long_description

    def render(self):
        """
        Print the description of the item to the console.
        """
        print(*textwrap.wrap(self._describe(), width=72), sep="\n")

    def short_render(self):
        """
        Show the friendly name of the item.
        """
        return self.friendly_name
