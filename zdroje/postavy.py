import queue
import random
from tkinter import PhotoImage

print(__name__)


class Character():
    def __init__(self, start_x, start_y, start_height, name, hp, armor, weapon, speed, canvas, img_set = None):

        ## Pozícia
        self.start_x, self.start_y = start_x, start_y
        self.x, self.y = start_x, start_y
        self.start_height = start_height
        self.height = start_height

        ## Predmety
        self.armor = armor
        self.weapon = weapon

        ## Štatistiky
        self.name = name
        self.base_hp = hp
        self.base_speed = speed

        ## Obrázky
        self.img_set = img_set
        self.canvas = canvas

        self.step_cooldown = 0
        self.direction = "right"


    def draw(self):
        self.character_img = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x + 80, self.start_y + 120, tags = "map")
        self.weapon_img = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x + 80, self.start_y + 120, outline = "blue", tags = "map")
        # self.armor_img = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x + 80, self.start_y + 120, fill = "white", outline = "red", tags = "map")


    def setSpeed(self):
        self.speed = self.base_speed - self.armor.speed_modifier - self.weapon.speed_modifier

class MainCharacter(Character):

    images_right = [PhotoImage(file = "zdroje/images/jack/jack_right_{}.gif".format(n)) for n in range(5)]
    images_left = [PhotoImage(file = "zdroje/images/jack/jack_left_{}.gif".format(n)) for n in range(4)]

    coin = PhotoImage(file = "zdroje/images/coin.gif")

    def __init__(self, start_x, start_y, start_height, hp, base_hp, armors, weapons, armor, weapon, speed, canvas, player_data, img_set = None):
        super().__init__(start_x, start_y, start_height, "Jack", hp, armor, weapon, speed, canvas, img_set)

        self.level_data = None
        self.player_data = player_data

        self.hp = self.player_data["parameters"]["hp"]

        self.armors = armors
        self.weapons = weapons

        self.armor = self.armors[armor]
        self.weapon = self.weapons[weapon]

        ## Skákanie
        self.offset = 0
        self.max_offset = 200
        self.jumping = False
        self.falling = False

        ## Invetár
        self.coins = self.player_data["parameters"]["coins"]

        ## Boj
        self.attack_cooldown = 0
        self.attacking = False
        self.last_attack = None
        self.move_left = False

        self.next = 1


        self.alive = True

    def draw(self):
        self.character_img = self.canvas.create_image(self.start_x, self.start_y, image = MainCharacter.images_right[0], anchor = "nw", tags = "map")
        self.armor_img = self.canvas.create_image(self.start_x, self.start_y, image = self.armor.images[0], anchor = "nw", tags = "map")
        self.weapon_img = self.canvas.create_image(self.start_x, self.start_y, image = self.weapon.images[0], anchor = "nw", tags = "map")

    def move(self, x):
        for img in (self.character_img, self.weapon_img, self.armor_img):
            self.canvas.move(img, x * self.speed / 4, 0)
        self.x += x * self.speed / 4


    ## SKÁKANIE A PADANIE

    def jump(self):
            if not self.falling:
                for img in (self.character_img, self.weapon_img, self.armor_img):
                    self.canvas.move(img, 0, -5)

                self.offset += 5

            elif self.falling:
                for img in (self.character_img, self.weapon_img, self.armor_img):
                    self.canvas.move(img, 0, 5)

                self.offset -= 5

            if self.offset == self.max_offset:
                self.falling = True

            if self.offset % 180 == 0 and self.offset // 180 <= self.level_data["level"]["max_height"] and self.falling:
                if self.fallChecker(self.platforms[self.offset // 180]):
                    self.falling = False
                    self.jumping = False
                    self.max_offset = self.offset + 200
                    self.height = self.offset // 180

    def fall(self):
        try:
            if not self.fallChecker(self.platforms[self.offset // 180]) and not self.jumping:
                self.falling = True
        except IndexError:
            pass

    def fallChecker(self, platform):
        cont = False
        for plat in platform:
            if plat[0] < self.x < plat[1]:
                cont = True
                break
            else:
                cont = False
        return cont


    ## BOJ

    def attack(self, enemies):

        if not self.attacking:
            self.attack_cooldown = 10
            self.attacking = True
            if self.direction == "right" or self.direction == "jright":
                self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[1])
            elif self.direction == "left" or self.direction == "jleft":
                self.move_left = True
                self.canvas.move(self.weapon_img, - 60, 0)
                self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[3])

            for enemy in enemies:
                if self.player_data["level_info"]["level"] != 4:
                    collision = (((abs(enemy.x - self.x - 80) <= self.weapon.reach) and (self.direction == "right" or self.direction == "jright")) or ((abs(enemy.x - self.x + 80) <= self.weapon.reach) and (self.direction == "left" or self.direction == "jleft"))) and (self.offset // 180 == enemy.height)
                else:
                    collision = ((abs(enemy.x - self.x - 80) <= self.weapon.reach) and (self.direction == "right" or self.direction == "jright")) or ((abs(enemy.x - self.x + 470) <= self.weapon.reach) and (self.direction == "left" or self.direction == "jleft"))
                if collision:
                    enemy.hp -= self.weapon.dmg
                    self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                    self.canvas.coords(enemy.hp_bar_1, (enemy.x, enemy.y - 28, enemy.x + (80 / enemy.base_hp * enemy.hp), enemy.y - 13))
                    if enemy.hp <= 0:
                        if enemy.alive:
                            self.changeCoins(enemy.loot)
                        for img in (enemy.character_img, enemy.weapon_img, enemy.hp_text, enemy.hp_bar_1, enemy.hp_bar_2):
                            enemy.canvas.delete(img)
                            enemy.alive = False
                            self.last_attack = None


                    else:
                        self.last_attack = enemy

        elif self.attacking:
            if self.direction == "right" or self.direction == "jright":
                self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[0])
            elif self.direction == "left" or self.direction == "jleft":
                self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[2])

            if self.move_left:
                self.canvas.move(self.weapon_img, 60, 0)
                self.move_left = False

            self.attacking = False
            if self.last_attack is not None:
                self.last_attack = None

    def createPlatforms(self):
        self.platforms = [list() for i in range(self.level_data["level"]["max_height"] + 1)]

        for platform in self.level_data["level"]["platforms"]:
            self.platforms[platform[0]].append((platform[1] - 80, platform[2]))

    def createParameters(self):
        self.top_bg = self.canvas.create_rectangle(0, 0, 1280, 50, fill = "white")

        self.hp_bar_1 = self.canvas.create_rectangle(31, 18.5, 30 + (180 / self.base_hp * self.hp), 32.5, fill = "green", outline = "green")
        self.hp_bar_2 = self.canvas.create_rectangle(30, 17.5, 210, 32.5)

        self.hp_text = self.canvas.create_text(120, 25, text = "{}/{}".format(self.hp, self.base_hp))


        self.coin_img = self.canvas.create_image(1180, 25, image = self.coin)
        self.coins_text = self.canvas.create_text(1150, 25, text = "{}".format(self.coins))

    def createArmors(self):
        self.armor_bar_1 = self.canvas.create_rectangle(211, 18.5, 210 + (50 / self.armor.base_armor * self.armor.armor), 32.5, fill = "lightblue", outline = "lightblue", tags = "armor")
        self.armor_bar_2 = self.canvas.create_rectangle(210, 17.5, 260, 32.5, tags = "armor")

        self.armor_text = self.canvas.create_text(235, 25, text = "{}/{}".format(self.armor.armor, self.armor.base_armor), tags = "armor")


    def changeCoins(self, amount):
        self.coins += amount
        self.canvas.itemconfig(self.coins_text, text = "{}".format(self.coins))

    def setAll(self):
        self.draw()
        self.setSpeed()
        self.createParameters()
        self.createArmors()
        self.createPlatforms()

class Monster(Character):
    def __init__(self, start_x, start_y, start_height, name, base_hp, armor, weapon, speed, canvas, loot, pattern_string, img_set = None):
        super().__init__(start_x, start_y, start_height, name, base_hp, armor, weapon, speed, canvas, img_set)

        self.loot = loot
        self.pattern_string = pattern_string

        self.hp = base_hp

        self.walking = True

        self.alive = True
        self.attack_cooldown = 20
        self.attacking = False
        self.attack_count = 5

        self.weapon_move = False
        self.weapon_move_ = False # kontroluje nech sa pohne len raz
        self.move_left = False

        self.step_count = 10
        self.step = 1
        self.last_step_image = 1
        self.last_step = 0

    def draw(self):
        self.character_img = self.canvas.create_image(self.start_x, self.start_y, image = self.images_left[0], anchor = "nw", tags = "map")
        self.weapon_img = self.canvas.create_image(self.start_x, self.start_y, image = self.weapon.images[0], anchor = "nw", tags = "map")


    def move(self, x):
        for img in (self.character_img, self.weapon_img, self.hp_text, self.hp_bar_1, self.hp_bar_2):
            self.canvas.move(img, x * self.speed / 4, 0)
        self.x += x * self.speed / 4

    def attack(self, enemy):
        if not self.attacking:
            self.attacking = True

            if self.direction == "right":
                self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[1])
            elif self.direction == "left":
                self.move_left = True
                self.canvas.move(self.weapon_img, - 60, 0)
                self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[3])


            if ((abs(enemy.x - self.x - 80) <= self.weapon.reach) or (abs(enemy.x - self.x + 80) <= self.weapon.reach)) and (self.height == enemy.offset // 180):
                    if enemy.hp - self.weapon.dmg <= 0:
                        enemy.alive = False
                    elif enemy.hp > 0:
                        if enemy.armor.armor > 0:
                            if enemy.armor.armor - self.weapon.dmg <= 0:
                                minus = abs(enemy.armor.armor - self.weapon.dmg)
                                enemy.armor.armor = 0
                                enemy.hp -= minus
                                self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                                self.canvas.coords(enemy.hp_bar_1, (31, 17.5, 30 + (180 / enemy.base_hp * enemy.hp), 32.5))
                            else:
                                enemy.armor.armor -= self.weapon.dmg
                        else:
                            enemy.hp -= self.weapon.dmg
                            self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                            self.canvas.coords(enemy.hp_bar_1, (31, 17.5, 30 + (180 / enemy.base_hp * enemy.hp), 32.5))

        else:
            if self.attack_count != 0:
                self.attack_count -= 1
            elif self.attack_count == 0:

                if self.direction == "right":
                    self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[0])
                elif self.direction == "left":
                    self.canvas.itemconfig(self.weapon_img, image = self.weapon.images[2])
                    self.canvas.move(self.weapon_img, 60, 0)

                if self.move_left:
                    self.move_left = False

                self.attacking = False
                self.attack_count = 5

    def setPattern(self):

        self.pattern = queue.Queue()
        [self.pattern.put(n) for n in self.pattern_string]

    def jackCheck(self, other):

        if (abs(self.x - other.x) <= 200) and (other.height == self.height):
            self.walking = False

        elif (abs(self.x - other.x) >= 200) and (other.height == self.height):
            self.walking = True

        if ((abs(other.x - self.x - 80) <= self.weapon.reach) or (abs(other.x - self.x + 80) <= self.weapon.reach)) and (self.height == other.height):
            if self.attack_cooldown == 0:
                self.attack_cooldown = 25
            else:
                self.attack_cooldown -= 1
        else:
            self.attack_cooldown = 25


    def hpText(self):
        self.hp_bar_2 = self.canvas.create_rectangle(self.x, self.y - 28, self.x + 80, self.y - 13, fill = "#FFF", outline = "#FFF",tags = "map")
        self.hp_bar_1 = self.canvas.create_rectangle(self.x, self.y - 28, self.x + 80, self.y - 13, fill = "red", outline = "red", tags = "map")

        self.hp_text = self.canvas.create_text(self.x + 40, self.y - 20, text = "{}/{}".format(self.hp, self.base_hp), tags = "map")

    def setAll(self):
        self.hpText()
        self.draw()
        self.setSpeed()
        self.setPattern()


    def animate_attack(self):
        pass


# Základné príšery

class Wolf(Monster):

    images_right = [PhotoImage(file = "zdroje/images/wolf/wolf_right_{}.gif".format(n)) for n in range(4)]
    images_left = [PhotoImage(file = "zdroje/images/wolf/wolf_left_{}.gif".format(n)) for n in range(4)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(5, 10)
        super().__init__(start_x, start_y, start_height, "Wolf", 20, armor, weapon, 10, canvas, loot, pattern_string, img_set)

    def draw(self):
        self.character_img = self.canvas.create_image(self.start_x, self.start_y, image = self.images_left[0], anchor = "nw", tags = "map")
        self.weapon_img = self.canvas.create_image(self.start_x, self.start_y, image = self.weapon.images[0], anchor = "nw", tags = "map", state = "hidden")

    def attack(self, enemy):
        if not self.attacking:

            self.attacking = True
            if ((abs(enemy.x - self.x - 80) <= self.weapon.reach) or (abs(enemy.x - self.x + 80) <= self.weapon.reach)) and (self.height == enemy.offset // 180):
                    if enemy.hp - self.weapon.dmg <= 0:
                        enemy.alive = False
                    elif enemy.hp > 0:
                        if enemy.armor.armor > 0:
                            if enemy.armor.armor - self.weapon.dmg <= 0:
                                minus = abs(enemy.armor.armor - self.weapon.dmg)
                                enemy.armor.armor = 0
                                enemy.hp -= minus
                                self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                                self.canvas.coords(enemy.hp_bar_1, (31, 17.5, 30 + (180 / enemy.base_hp * enemy.hp), 32.5))
                            else:
                                enemy.armor.armor -= self.weapon.dmg

                            self.canvas.itemconfig(enemy.armor_text, text = "{}/{}".format(enemy.armor.armor, enemy.armor.base_armor))
                            self.canvas.coords(enemy.armor_bar_1, (211, 17.5, 210 + (50 / enemy.armor.base_armor * enemy.armor.armor), 32.5))
                            enemy.player_data["parameters"]["armor"] = enemy.armor.armor
                        else:
                            enemy.hp -= self.weapon.dmg
                            self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                            self.canvas.coords(enemy.hp_bar_1, (31, 17.5, 30 + (180 / enemy.base_hp * enemy.hp), 32.5))


            if self.direction == "left":
                self.canvas.move(self.character_img, -40, 0)
                self.canvas.itemconfig(self.character_img, image = self.images_left[3])
            elif self.direction == "right":
                self.canvas.move(self.character_img, 40, 0)
                self.canvas.itemconfig(self.character_img, image = self.images_right[3])

        else:
            if self.attack_count != 0:
                self.attack_count -= 1
            elif self.attack_count == 0:
                if self.direction == "left":
                    self.canvas.move(self.character_img, 40, 0)
                    self.canvas.itemconfig(self.character_img, image = self.images_left[0])
                elif self.direction == "right":
                    self.canvas.move(self.character_img, -40, 0)
                    self.canvas.itemconfig(self.character_img, image = self.images_right[0])
                self.attack_count = 5
                self.attacking = False

class Goblin(Monster):

    images_right = [PhotoImage(file = "zdroje/images/goblin/goblin_right_{}.gif".format(n)) for n in range(3)]
    images_left = [PhotoImage(file = "zdroje/images/goblin/goblin_left_{}.gif".format(n)) for n in range(3)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(15, 25)
        super().__init__(start_x, start_y, start_height, "Goblin", 40, armor, weapon, 5, canvas, loot, pattern_string, img_set)

class Skeleton(Monster):

    images_right = [PhotoImage(file = "zdroje/images/skeleton/skeleton_right_{}.gif".format(n)) for n in range(3)]
    images_left = [PhotoImage(file = "zdroje/images/skeleton/skeleton_left_{}.gif".format(n)) for n in range(3)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(30, 40)
        super().__init__(start_x, start_y, start_height, "Skeleton", 60, armor, weapon, 8, canvas, loot, pattern_string, img_set)


# Mini-boss

class SuperWolf(Monster):

    images_right = [PhotoImage(file = "zdroje/images/wolf/wolf_right_{}.gif".format(n)) for n in range(4)]
    images_left = [PhotoImage(file = "zdroje/images/wolf/wolf_left_{}.gif".format(n)) for n in range(4)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(50, 60)
        super().__init__(start_x, start_y, start_height, "Super Wolf", 50, armor, weapon, 10, canvas, loot, pattern_string, img_set)

    def draw(self):
        Wolf.draw(self)

    def attack(self, enemy):
        Wolf.attack(self, enemy)

class SuperGoblin(Monster):

    images_right = [PhotoImage(file = "zdroje/images/goblin/goblin_right_{}.gif".format(n)) for n in range(3)]
    images_left = [PhotoImage(file = "zdroje/images/goblin/goblin_left_{}.gif".format(n)) for n in range(3)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(100, 120)
        super().__init__(start_x, start_y, start_height, "SuperGoblin", 80, armor, weapon, 7, canvas, loot, pattern_string, img_set)

class SuperSkeleton(Monster):

    images_right = [PhotoImage(file = "zdroje/images/skeleton/skeleton_right_{}.gif".format(n)) for n in range(3)]
    images_left = [PhotoImage(file = "zdroje/images/skeleton/skeleton_left_{}.gif".format(n)) for n in range(3)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(100, 120)
        super().__init__(start_x, start_y, start_height, "SuperGoblin", 150, armor, weapon, 10, canvas, loot, pattern_string, img_set)


# Boss

class Dragon(Monster):

    images_right = [PhotoImage(file = "zdroje/images/dragon/dragon_right_{}.gif".format(n)) for n in range(4)]
    images_left = [PhotoImage(file = "zdroje/images/dragon/dragon_left_{}.gif".format(n)) for n in range(4)]

    def __init__(self, start_x, start_y, start_height, armor, weapon, pattern_string, canvas, img_set = None):
        loot = random.randint(1000, 2000)
        super().__init__(start_x, start_y, start_height, "Dragon", 500, armor, weapon, 5, canvas, loot, pattern_string, img_set)

        self.move_l = False

    def draw(self):
        self.character_img = self.canvas.create_image(self.start_x, self.start_y, image = self.images_left[0], anchor = "nw", tags = "map")
        self.weapon_img = self.canvas.create_image(self.start_x, self.start_y, image = self.weapon.images[0], anchor = "nw", tags = "map", state = "hidden")

    # def hpText(self):
    #     self.hp_bar_2 = self.canvas.create_rectangle(self.x, self.y - 348, self.x + 80, self.y - 333, fill = "#FFF", outline = "#FFF",tags = "map")
    #     self.hp_bar_1 = self.canvas.create_rectangle(self.x, self.y - 348, self.x + 80, self.y - 333, fill = "red", outline = "red", tags = "map")
    #
    #     self.hp_text = self.canvas.create_text(self.x + 40, self.y - 340, text = "{}/{}".format(self.hp, self.base_hp), tags = "map")

    def attack(self, enemy):
        if not self.attacking:
            self.attacking = True
            if ((abs(enemy.x - self.x - 80) <= self.weapon.reach) or (abs(enemy.x - self.x + 80) <= self.weapon.reach)) and (self.height == enemy.offset // 180):
                    if enemy.hp > 0:
                        if enemy.armor.armor > 0:
                            if enemy.armor.armor - self.weapon.dmg <= 0:
                                minus = abs(enemy.armor.armor - self.weapon.dmg)
                                enemy.armor.armor = 0
                                enemy.hp -= minus
                                self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                                self.canvas.coords(enemy.hp_bar_1, (31, 17.5, 30 + (180 / enemy.base_hp * enemy.hp), 32.5))
                            else:
                                enemy.armor.armor -= self.weapon.dmg

                            self.canvas.itemconfig(enemy.armor_text, text = "{}/{}".format(enemy.armor.armor, enemy.armor.base_armor))
                            self.canvas.coords(enemy.armor_bar_1, (211, 17.5, 210 + (50 / enemy.armor.base_armor * enemy.armor.armor), 32.5))
                            enemy.player_data["parameters"]["armor"] = enemy.armor.armor
                        else:
                            if enemy.hp - self.weapon.dmg <= 0:
                                enemy.hp = 0
                            else:
                                enemy.hp -= self.weapon.dmg
                            self.canvas.itemconfig(enemy.hp_text, text = "{}/{}".format(enemy.hp, enemy.base_hp))
                            self.canvas.coords(enemy.hp_bar_1, (31, 17.5, 30 + (180 / enemy.base_hp * enemy.hp), 32.5))
            if self.direction == "left":
                self.canvas.itemconfig(self.character_img, image = self.images_left[3])
                self.canvas.move(self.character_img, -450, 0)
                self.move_l = True
            elif self.direction == "right":
                self.canvas.itemconfig(self.character_img, image = self.images_right[3])

        else:
            if self.attack_count != 0:
                self.attack_count -= 1
            elif self.attack_count == 0:

                if self.direction == "left":
                    self.canvas.itemconfig(self.character_img, image = self.images_left[0])
                    self.canvas.move(self.character_img, 450, 0)
                    self.move_l = False

                elif self.direction == "right":
                    self.canvas.itemconfig(self.character_img, image = self.images_right[0])

                self.attack_count = 5
                self.attacking = False
