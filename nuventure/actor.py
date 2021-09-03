from nuventure.world import World, Node
from nuventure.item import Item

actor_types = {"player", "npc"}


class Actor:
    def __init__(self, bound_world: World, location: Node, name="Adventurer", hp=100, actor_type="player", movement_rate=1):
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
            actor_type: the type of actor this is (player or NPC)
            movement_rate: the actor's movement rate (defaults to 1 node per gametic)
        """
        self.name = name
        self.bound_world = bound_world
        self.location = location
        self.hit_points = hp
        self.inventory = {}

        if actor_type in actor_types:
            self.actor_type = actor_type
        else:
            raise KeyError(f"invalid actor type for actor {self.name}")

        self.movement_rate = movement_rate

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
        result = self.bound_world.try_move(self, direction)
        if result:
            self.location.render()
        return result

    def add_item(self, item: Item):
        self.inventory[item.internal_name] = item

    def drop_item(self, item: Item):
        if self.inventory.get(item.internal_name):
            item.drop(self)
            print(
                f"You remove the f{item.friendly_name} from your pack and set it aside.")
            del self.inventory[item.internal_name]
            return f"Dropped {item.internal_name}."
