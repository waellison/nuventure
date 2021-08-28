"""Classes for Nuventure, a Python-based interactive fiction engine."""


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

        if(dbinfo["itemsPresentOnLoad"] != None):
            self.items += dbinfo["itemsPresentOnLoad"]

        while dbinfo["linkedNodes"]:
            neighbor = dbinfo["linkedNodes"].pop()
            self.neighbors[neighbor["direction"]] = {
                "name": neighbor["name"],
                "travel_description": neighbor["travelDescription"]
            }

    def __str__(self):
        """Returns the node's internal name."""
        return self.internal_name

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


class World:
    def __init__(self, pathname="./world.json"):
        """Creates a new game world, populating its nodes.

        Args:
            pathname: The world info JSON file to load from disk.
        """
        self.nodes = dict()
        fh = open(pathname, "r")
        rawdata = json.load(fh)
        fh.close()

        for key, value in rawdata["mapNodes"].items():
            self.nodes[key] = Node(key, value)

    def try_move(self, actor, direction):
        """Attempts to move an actor within the world.

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
                travel_description = loc.neighbors[direction]["travel_description"]
                dest_node = self.nodes[loc.neighbors[direction]["name"]]
                actor.location = dest_node
                print(*textwrap.wrap(travel_description, 72), sep="\n")
                return True
            else:
                return False


class Actor:
    def __init__(self, bound_world: World, location: Node, name="Adventurer", hp=100):
        """Create a new actor object.

        An Actor is a character entity in the game world, such as the player
        or an NPC.  An Actor is bound to the world that it occupies and
        to the node it currently occupies within that world, as of the
        current gametic.

        Args:
            bound_world: the world object to which this actor is bound
            location: the node within the world where this actor is currently located
            name: the name of this actor (defaults to "Adventurer")
            hp: the amount of hit points to give this character (defaults to 100)
        """
        self.name = name
        self.bound_world = bound_world
        self.location = location
        self.hit_points = hp

    def __str__(self):
        """Returns the actor's name."""
        return self.name

    def injure(self, amount=5):
        """Injures an actor, detracting the specified amount of HP.

        Arguments:
            amount: the amount by which to reduce the actor's
                health (defaults to 5)
        """
        self.hit_points -= amount

    def is_dead(self):
        """Returns whether the character is dead."""
        return self.hit_points == 0

    def move(self, direction):
        """Attempts to move the actor within the world map.

        Args:
            direction: The direction in which to attempt to move the character.

        Returns:
            True if movement succeeded, False if not, None if the movement verb
            was invalid.
        """
        return self.bound_world.try_move(self, direction)


class Verb:
    def __init__(self, name, invokerActor, boundWorld, boundItem=None, targetActor=False):
        """Creates a new verb object.

        Verbs represent permissible actions in the Nuventure engine.  A given Verb
        is bound to the actor that invokes it, the world object in which it is invoked,
        and the item and target, if needed.
        """
        self.name = name
        self.invoker = invokerActor
        self.world = boundWorld
        self.bound_item = boundItem
        self.target = targetActor

    def callback(self):
        return None


class Parser:
    def __init__(self, verbtable="./verbs.json"):
        fh = open(verbtable, "r")
        db = json.load(fh)
        fh.close

# TODO: Start to write classes for the various verbs, all inheriting from Verb.
# See if there is a way to reference these from the JSON.
