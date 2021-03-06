"""World module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import json
from nuventure import nv_print
from nuventure.item import NVItem, NVWeapon, NVSpellbook, NVLamp
from nuventure.actor import NVActor


class NVWorldNode:
    """
    A map node is a point on the map to which an Actor may travel.
    Nodes contain various internal state including a list of neighbor
    nodes, which in technical terms is a directed graph.
    """

    def __init__(self, i_name: str, dbinfo: dict):
        """Create a new map node.

        Args:
            i_name: the internal name of the node, from the JSON file
            dbinfo: the information from the JSON file regarding this node
        """
        self.internal_name = i_name
        self.friendly_name = dbinfo["friendlyName"]
        self.items = []
        self.neighbors = {}
        self.descriptions = {}
        self.npcs = []
        self.visited_p = False
        self.wanted_state = dbinfo["requiresState"]

        self.descriptions["long"] = dbinfo["longDescription"]
        self.descriptions["short"] = dbinfo["shortDescription"]
        self.descriptions["long_stateful"] = dbinfo["longDescriptionWithState"]
        self.descriptions["short_stateful"] = dbinfo["shortDescriptionWithState"]

        while dbinfo["linkedNodes"]:
            neighbor = dbinfo["linkedNodes"].pop()
            self.neighbors[neighbor["direction"]] = {
                "name": neighbor["name"],
                "travel_description": neighbor["travelDescription"],
            }

    def __str__(self) -> str:
        """Returns the node's internal name."""
        return self.internal_name

    def render(self, long_p: bool = False, stateful_p: bool = False) -> None:
        """Print an appropriate description of the given node.

        If the node is marked as visited, then we want the brief description,
        else we want the long one, and in all cases we want the items in the
        scene.

        Args:
            long_p: True if the long description should be printed, False
                otherwise.
            stateful_p: True if the description should be the one triggered by
                the required state, False otherwise."""
        length = "long" if long_p or not self.visited_p else "short"
        print("")
        nv_print(self.friendly_name)
        nv_print(self.describe(length, stateful_p))

        if self.npcs:
            print("")
            for actor in self.npcs:
                nv_print(actor.description)

        if self.items:
            print("")
            for item in self.items:
                nv_print(item.look_description)

    def describe(self, length: str = "long", stateful_p: bool = False) -> str:
        """Returns a description of the given node.

        Nodes have either two or four descriptions: a long description to be
        printed upon invoking the "look" command or visiting the node for the
        first time, and a short description to be printed for a node that has
        been visited before, upon revisiting it.

        The stateful descriptions, triggered by calling this method with
        stateful_p set to True, are printed when entering the node with the
        required state (Node.required_state) activated, e.g. when the player's
        lamp is turned on and the player enters a darkened cell.

        Arguments:
            length: one of "long" or "short", indicating the desired length
            stateful_p: whether this is the description to be printed
                after the required state of this node is triggered
                (defaults to False)

        Returns:
            The selected description of the node as a string.
        """
        if stateful_p is True:
            return self.descriptions[f"{length}_stateful"]

        return self.descriptions[length]

    def add_item(self, item: NVItem) -> None:
        """Adds an item to the given node.

        Args:
            item: the item to add"""
        self.items.append(item)


class NVWorld:
    """
    NVWorld represents the world where the game takes place.  A world
    consists of its nodes, items, and actors.
    """

    def __init__(self, game_instance, pathname="./world.json"):
        """Creates a new game world, populating its nodes.

        Args:
            pathname: The world info JSON file to load from disk.
        """
        self.nodes = {}
        self.items = {}
        self.actors = {}

        with open(pathname, "r") as fh:
            rawdata = json.load(fh)

        for key, value in rawdata["mapNodes"].items():
            self.nodes[key] = NVWorldNode(key, value)

        for key, value in rawdata["npcs"].items():
            movement_rate = value["movementRate"]
            where = self.nodes[value["originCell"]]
            i_name = key
            f_name = value["friendlyName"]

            actor = NVActor(self, where, i_name, f_name, 100, movement_rate)
            actor.description = value["inSceneDescription"]
            self.actors[i_name] = actor
            self.nodes[value["originCell"]].npcs.append(actor)

        for key, value in rawdata["items"].items():
            i_types = {"lamp": NVLamp, "weapon": NVWeapon, "spellbook": NVSpellbook}
            klass = i_types.get(value["type"], NVItem)
            self.items[key] = klass(key, value, self)

        self.game_instance = game_instance

    def add_actor(self, actor) -> None:
        """Adds an actor to the world.

        Args:
            actor: the Actor object to add"""
        self.actors[actor.internal_name] = actor

    def try_move(self, actor: NVActor, direction: str) -> bool:
        """Attempts to move an actor within the world.

        Arguments:
            actor: the actor to attempt to move
            direction: the direction in which to attempt to move that actor
        """
        loc = actor.location

        if direction in loc.neighbors:
            destination_node = self.nodes[loc.neighbors[direction]["name"]]
            actor.location = destination_node
            return True

        return False

    def do_world_tic(self):
        """Do a tic within the world.

        For each gametic, actors may move the number of nodes specified by
        their movement rate.  Movement direction is randomly chosen per move.
        """
        for actor in self.actors.values():
            actor.do_tic()
