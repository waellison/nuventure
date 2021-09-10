"""World module for Nuventure, a poor man's implementation of ScummVM.

https://github.com/tnwae/nuventure

Copyright (c) 2021 by William Ellison.
<waellison@gmail.com>

Nuventure is licensed under the terms of the MIT License, furnished
in the LICENSE file at the root directory of this distribution.
"""

import textwrap
import json
import random
from nuventure.item import NVItem, NVWeapon, NVSpellbook, NVLamp


class NVWorldNode:
    """
    A map node is a point on the map to which an Actor may travel.
    Nodes contain various internal state including a list of neighbor
    nodes, which in technical terms is a directed graph.
    """

    def __init__(self, iname: str, dbinfo: dict):
        """Create a new map node.

        Args:
            iname: the internal name of the node, from the JSON file
            dbinfo: the information from the JSON file regarding this node
        """
        self.internal_name = iname
        self.friendly_name = dbinfo["friendlyName"]
        self.items = []
        self.neighbors = {}
        self.descriptions = {}
        self.visitedp = False
        self.wanted_state = dbinfo["requiresState"]

        self.descriptions["long"] = dbinfo["longDescription"]
        self.descriptions["short"] = dbinfo["shortDescription"]
        self.descriptions["long_stateful"] = dbinfo["longDescriptionWithState"]
        self.descriptions["short_stateful"] = dbinfo["shortDescriptionWithState"]

        while dbinfo["linkedNodes"]:
            neighbor = dbinfo["linkedNodes"].pop()
            self.neighbors[neighbor["direction"]] = {
                "name": neighbor["name"],
                "travel_description": neighbor["travelDescription"]
            }

    def __str__(self):
        """Returns the node's internal name."""
        return self.internal_name

    def render(self, longp=False, statefulp=False):
        """Print an appropriate description of the given node.

        If the node is marked as visited, then we want the brief description,
        else we want the long one, and in all cases we want the items in the
        scene.

        Args:
            longp: True if the long description should be printed, False
                otherwise.
            statefulp: True if the description should be the one triggered by
                the required state, False otherwise."""
        length = "long" if longp or not self.visitedp else "short"
        print(self.friendly_name)
        print(*textwrap.wrap(self.describe(length, statefulp)), sep="\n")

        for item in self.items:
            print(item.look_description)

    def describe(self, length="long", statefulp=False):
        """Prints a description of the given node.

        Nodes have either two or four descriptions: a long description to be
        printed upon invoking the "look" command or visiting the node for the
        first time, and a short description to be printed for a node that has
        been visited before, upon revisiting it.

        The stateful descriptions, triggered by calling this method with
        statefulp set to True, are printed when entering the node with the
        required state (Node.required_state) activated, e.g. when the player's
        lamp is turned on and the player enters a darkened cell.

        Arguments:
            length: one of "long" or "short", indicating the desired length
            statefulp: whether this is the description to be printed
                after the required state of this node is triggered
                (defaults to False)
        """
        if statefulp is True:
            return self.descriptions[f"{length}_stateful"]
        else:
            return self.descriptions[length]

    def add_item(self, item: NVItem):
        """Adds an item to the given node.

        Args:
            item: the item to add"""
        self.items.append(item)


class NVWorld:
    def __init__(self, game_instance, pathname="./world.json"):
        """Creates a new game world, populating its nodes.

        Args:
            pathname: The world info JSON file to load from disk.
        """
        self.nodes = {}
        self.items = {}

        with open(pathname, "r") as fh:
            rawdata = json.load(fh)

        for key, value in rawdata["mapNodes"].items():
            self.nodes[key] = NVWorldNode(key, value)

        for key, value in rawdata["items"].items():
            itypes = {
                "lamp": NVLamp,
                "weapon": NVWeapon,
                "spellbook": NVSpellbook
            }
            klass = itypes.get(value["type"], NVItem)

            self.items[key] = klass(key, value, self)

        self.actors = []
        self.game_instance = game_instance

    def add_actor(self, actor):
        """Adds an actor to the world.

        Args:
            actor: the Actor object to add"""
        self.actors.append(actor)

    def try_move(self, actor, direction):
        """Attempts to move an actor within the world.

        Arguments:
            actor: the actor to attempt to move
            direction: the direction in which to attempt to move that actor
        """
        loc = actor.location

        if direction in loc.neighbors:
            dest_node = self.nodes[loc.neighbors[direction]["name"]]
            actor.location = dest_node
            return True
        else:
            return False

    def do_world_tic(self):
        """Do a tic within the world.

        For each gametic, actors may move the number of nodes specified by
        their movement rate.  Movement direction is randomly chosen per move.
        """
        for actor in self.actors:
            if actor == self.game_instance.player:
                continue

            for _ in range(0, actor.movement_rate):
                directions = actor.location.neighbors.keys()
                thisway = random.choice(directions)
                movement = self.game_instance.parser.verbs[thisway]
                movement.invoker = actor
                movement.invoke()
