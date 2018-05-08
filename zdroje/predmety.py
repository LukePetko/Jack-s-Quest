from tkinter import PhotoImage

print(__name__)


class Item():
    def __init__(self, _name, name, speed_modifier, price, is_armor, img_set = None):

        ## Zmeny postáv
        self.speed_modifier = speed_modifier

        ## Charakterizácia
        self.name = name
        self._name = _name
        self.price = price
        self.is_armor = is_armor

        ## Obrázky
        self.img_set = img_set


class Weapon(Item):
    def __init__(self, _name, name, dmg, reach, speed_modifier, price, is_armor, img_set):
        super().__init__(_name, name, speed_modifier, price, is_armor, img_set)

        self.reach = reach
        self.dmg = dmg

        self.images = []

        for i in range(6):
            self.images.append(PhotoImage(file = "zdroje/images/{}/{}.gif".format(img_set, i)))


class Armor(Item):
    def __init__(self, _name, name, armor, speed_modifier, price, is_armor, img_set = None):
        super().__init__(_name, name, speed_modifier, price, is_armor, img_set)

        self.armor = armor
        self.base_armor = armor

        self.images = []

        for i in range(3):
            self.images.append(PhotoImage(file = "zdroje/images/{}/{}.gif".format(img_set, i)))
