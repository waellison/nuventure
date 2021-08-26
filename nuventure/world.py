"""
The World class for Nuventure, and related classes.
"""

import json


class Node:
    def __init__(self, iname, dbinfo):
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
        return self.internal_name


class World:
    nodes = dict()

    def __init__(self, pathname="./world.json"):
        fh = open(pathname, "r")
        rawdata = json.load(fh)
        fh.close()

        for key, value in rawdata["mapNodes"].items():
            self.nodes[key] = Node(key, value)

        for node in self.nodes:
            print(f"{node}'s neighbors:")

            for direction, edge in self.nodes[node].neighbors.items():
                print(f"\t{direction}: {edge['name']}")
