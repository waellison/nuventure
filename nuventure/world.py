"""
The World class for Nuventure, and related classes.
"""

import json


class Node:
    def __init__(self, iname, dbinfo):
        """Create a new map node.

        Arguments:
        iname: the internal name of the node, from the JSON file
        dbinfo: the information from the JSON file regarding this node
        """
        self.internal_name = iname
        self.friendly_name = dbinfo["friendlyName"]
        self.items = []
        self.neighbors = {}
        self.descriptions = {}

        self.descriptions["long"] = dbinfo["longDescription"]
        self.descriptions["short"] = dbinfo["shortDescription"]
        self.descriptions["long_stateful"] = dbinfo["longDescriptionWithState"]
        self.descriptions["short_stateful"] = dbinfo["shortDescriptionWithState"]

        if(dbinfo["itemsPresentOnLoad"] != None):
            self.items += dbinfo["itemsPresentOnLoad"]

        while dbinfo["linkedNodes"]:
            neighbor = dbinfo["linkedNodes"].pop()
            self.neighbors[neighbor["direction"]] = {
                "name": neighbor["name"],
                "travel_description": neighbor["travelDescription"]
            }

    def __str__(self):
        """Stringize a node, returning its internal name."""
        return self.internal_name


class World:
    nodes = dict()

    def __init__(self, pathname="./world.json"):
        """Create a new game world, populating its nodes.

        Arguments:
        pathname: The world info JSON file to load from disk
        """
        fh = open(pathname, "r")
        rawdata = json.load(fh)
        fh.close()

        for key, value in rawdata["mapNodes"].items():
            self.nodes[key] = Node(key, value)

        for node in self.nodes:
            print(f"{node}'s neighbors:")

            for direction, edge in self.nodes[node].neighbors.items():
                print(f"\t{direction}: {edge['name']}")

    def try_move(self, actor, direction):
        """Attempt to move an actor within the world.

        Arguments:
        actor: the actor to attempt to move
        direction: the direction in which to attempt to move that actor
        """
        valid_directions = {"east", "down", "up", "north", "west", "south"}

        if not(direction in valid_directions):
            return None
        else:
            loc = actor.location

            if direction in loc.neighbors:
                dest_node = self.nodes[loc.neighbors[direction]["name"]]
                actor.location = dest_node
                return True
            else:
                return False
