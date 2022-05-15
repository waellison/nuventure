"""Item module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

from nuventure import nv_print


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

        self.location = world.nodes.get(dbinfo["originCell"], None)

        if dbinfo["originOwner"]:
            self.owner = world.actors.get(dbinfo["originOwner"], None)
            self.owner.inventory[iname] = self

        if self.location:
            self.location.items.append(self)

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
            nv_print(f"You cannot take the {self.friendly_name}.")
        else:
            nv_print(self.take_description)
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
        nv_print(self._describe())

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
        """Trigger the lit state of the lamp."""
        if self.lit_state:
            self.lit_state = False
            nv_print(self.use_description[1])
        else:
            self.lit_state = True
            nv_print(self.use_description[0])

    def is_lit(self):
        """Return whether the lamp is lit."""
        return self.lit_state


class NVWeapon(NVItem):
    """
    A Weapon is an item that allows the player to harm non-player characters.
    """

    def __init__(self, iname: str, dbinfo: dict, world):
        """
        Create a new weapon.
        """
        super().__init__(iname, dbinfo, world)
        try:
            self.power = dbinfo["power"]
            self.print_on_use = dbinfo["inducesState"][0]["description"]
        except KeyError:
            nv_print(
                "error: cannot init a weapon without specifying attack power or use string")

    def use(self, other):
        """Use the weapon on the specified actor."""
        if not other:
            return -1

        other.injure(self.power)
        return self.power


class NVSpellbook(NVItem):
    """
    A Spellbook is an item that allows the player to learn a spell.
    It is consumed upon use.
    """

    def __init__(self, iname: str, dbinfo: dict, world):
        """
        Create a new spellbook.
        """
        super().__init__(iname, dbinfo, world)
        self.info = dbinfo
        self.spell = None

    def use(self, user):
        """Confer the spell in the spellbook on the user, if the user does
        not already know it."""
        if self.spell not in user.spells:
            if user.confer_spell(self.spell):
                return user.drop(self)
        return False
