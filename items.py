
class Item:
    """
    Item object representing the products and upgrades
    """
    def __init__(self, name, cost, location, type):
        self.name = name
        self.x = location[0]
        self.y = location[1]
        self.cost = cost
        self.type = ""
        self.count = 0
        self.increase = cost / 300
        self.cps = 0
        self.upgrades = None
        self.type = type


