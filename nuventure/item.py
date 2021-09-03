class Item:
    def __init__(self, iname: str, dbinfo: dict, world):
        self.internal_name = iname
        self.friendly_name = dbinfo["friendlyName"]
        self.look_description = dbinfo["inSceneDescription"]
        self.long_description = dbinfo["longDescription"]
        self.take_description = dbinfo["takeDescription"] or None
        self.map_node = world.nodes[dbinfo["originCell"]]
        self.owner = None
        self.map_node.add_item(self)

    def take(self, taker):
        if not self.take_description:
            print(f"You cannot take the {self.friendly_name}.")
        else:
            print(self.take_description)
            taker.add_item(self)
            self.owner = taker
            self.map_node.items.remove(self)
            self.map_node = None

    def drop(self, giver):
        self.owner = None
        self.map_node = giver.location
        self.map_node.items.append(self)

    def __str__(self):
        return self.internal_name

    def describe(self):
        return self.long_description

    def render(self):
        return self.look_description

    def short_render(self):
        return self.friendly_name
