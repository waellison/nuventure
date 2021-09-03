class Item:
    def __init__(self, iname: str, dbinfo: dict, world):
        self.internal_name = iname
        self.friendly_name = dbinfo["friendlyName"]
        self.look_description = dbinfo["inSceneDescription"]
        self.long_description = dbinfo["longDescription"]
        self.is_inventoryable = True if dbinfo["takeDescription"] else False
        self.map_node = world.nodes[dbinfo["originCell"]]
        self.owner = None
        self.map_node.add_item(self)

    def take(self, taker):
        if not self.is_inventoryable:
            print(f"You cannot take the {self.friendly_name}.")
        else:
            taker.add_item(self)
            self.owner = taker
            self.map_node.items.remove(self)
            self.map_node = None

    def drop(self, giver):
        giver.drop_item(self)
        self.owner = None
        self.map_node = giver.location

    def __str__(self):
        return self.internal_name

    def describe(self):
        return self.long_description

    def render(self):
        return self.look_description
