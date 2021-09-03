from nuventure.item import Item
import textwrap
import json


class Node:
    def __init__(self, iname: str, dbinfo: dict):
        """Create a new map node.

        A map node is a point on the map to which an Actor may travel.
        Nodes contain various internal state including a list of neighbor
        nodes, which in technical terms is a directed graph.

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

    def render(self, statefulp=False):
        length = "long" if not self.visitedp else "short"
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

    def add_item(self, item: Item):
        self.items.append(item)


class World:
    def __init__(self, pathname="./world.json"):
        """Creates a new game world, populating its nodes.

        Args:
            pathname: The world info JSON file to load from disk.
        """
        self.nodes = {}
        self.items = {}
        fh = open(pathname, "r")
        rawdata = json.load(fh)
        fh.close()

        for key, value in rawdata["mapNodes"].items():
            self.nodes[key] = Node(key, value)

        for key, value in rawdata["items"].items():
            self.items[key] = Item(key, value, self)

        self.actors = []

    def add_actor(self, actor):
        self.actors.append(actor)

    def try_move(self, actor, direction):
        """Attempts to move an actor within the world.

        Arguments:
            actor: the actor to attempt to move
            direction: the direction in which to attempt to move that actor
        """
        loc = actor.location

        if direction in loc.neighbors:
            travel_description = loc.neighbors[direction]["travel_description"]
            dest_node = self.nodes[loc.neighbors[direction]["name"]]
            actor.location = dest_node
            print(*textwrap.wrap(travel_description, 72), sep="\n")
            print("")
            return True
        else:
            return False
