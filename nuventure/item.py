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
        self.use_description = [
            dbinfo["useDescription"], dbinfo["useAltDescription"]]
        self.location = world.nodes[dbinfo["originCell"]]
        self.owner = None
        self.location.add_item(self)

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
            self.location.items.remove(self)
            self.location = None

    def drop(self, giver):
        """Drop an item back into the world, taking it from the
        actor giving it back to the world.

        Args:
            giver: the actor dropping the item

        Returns:
            Nothing.

        See Also:
            NVActor.drop_item"""
        self.owner = None
        self.location = giver.location
        self.location.items.append(self)

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


class NVLamp(NVItem):
    """
    A Lamp is an item that provides light in dark areas.
    """

    def __init__(self, iname: str, dbinfo: dict, world):
        """
        Create a new lamp.  The lit state starts as false.
        """
        super().__init__(iname, dbinfo, world)
        self.lit_state = False

    def use(self):
        if self.lit_state:
            self.lit_state = False
            print(*textwrap.wrap(self.use_description[1], width=72), sep="\n")
        else:
            self.lit_state = True
            print(*textwrap.wrap(self.use_description[0], width=72), sep="\n")

    def is_lit(self):
        return self.lit_state


class NVWeapon(NVItem):
    def __init__(self, iname: str, dbinfo: dict, world):
        super().__init__(iname, dbinfo, world)
        try:
            self.power = dbinfo["power"]
            self.print_on_use = dbinfo["inducesState"][0]["description"]
        except KeyError:
            print(
                "error: cannot init a weapon without specifying attack power or use string")

    def use(self, other):
        if not other:
            return -1
        else:
            other.injure(self.power)
            return self.power


class NVSpellbook(NVItem):
    def __init__(self, iname: str, dbinfo: dict, world):
        super().__init__(iname, dbinfo, world)
        self.info = dbinfo
        self.spell = None

    def use(self, user):
        if self.spell not in user.spells:
            return user.confer_spell(self.spell)
        else:
            return False
