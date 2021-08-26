class ActorIsDeadException(Exception):
    def __init__(self, expr, message):
        self.expression = expr
        self.message = message


class Actor:
    def __init__(self, bound_world, location, name="Adventurer"):
        self.name = name
        self.bound_world = bound_world
        self.location = location
        self.hit_points = 100

    def __str__(self):
        return self.name

    def injure(self, amount=5):
        self.hit_points -= amount
        if self.hit_points == 0:
            raise ActorIsDeadException(
                expr=None, message=f"{self.name} has died")

    def move(self, direction):
        return self.bound_world.try_move(self, direction)
