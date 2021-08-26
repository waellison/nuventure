class Actor:
    def __init__(self, bound_world, location, name="Adventurer", hp=100):
        """Create a new actor object.

        Arguments:
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
        """Stringize an actor object, returning its name."""
        return self.name

    def injure(self, amount=5):
        """Injure an actor, detracting the specified amount of HP.

        Arguments:
        amount: the amount by which to reduce the actor's health (defaults to 5)
        """
        self.hit_points -= amount

    def is_dead(self):
        return self.hit_points == 0

    def move(self, direction):
        """Attempt to move the actor within the world map.

        Arguments:
        direction: The direction in which to attempt to move the character.

        Returns:
        True if movement succeeded, False if not, None if the movement verb was invalid.
        """
        return self.bound_world.try_move(self, direction)
