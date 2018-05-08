import tkinter
import json

print(__name__)

root = tkinter.Tk()

from zdroje import postavy, predmety, patterns

def main():
    global game_canvas, pressed, level, stage, jack, main_game, end_screen, end_bool

    if main_game:

        if pressed["d"] and right_check():
            if right_check:
                jack.move(1)
                jack.fall()
            if (jack.direction in ("left", "jright")) and (not jack.jumping and not jack.falling):
                jack.step_cooldown += 1
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_right[0])
                game_canvas.itemconfig(jack.armor_img, image = jack.armor.images[0])
                if jack.direction == "left":
                    game_canvas.itemconfig(jack.weapon_img, image = jack.weapon.images[0])
                    game_canvas.move(jack.weapon_img, 8, 0)
                jack.direction = "right"
                jack.step_cooldown = 9

            elif (jack.direction in ("right", "jleft")) and (jack.jumping or jack.falling):
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_right[3])
                game_canvas.itemconfig(jack.armor_img, image = jack.armor.images[0])
                if jack.direction == "jleft":
                    game_canvas.itemconfig(jack.weapon_img, image = jack.weapon.images[0])
                    game_canvas.move(jack.weapon_img, 8, 0)
                jack.direction = "jright"
            jack.step_cooldown += 1

        if pressed["a"] and left_check():
            if jack.x > 0:
                jack.move(-1)
                jack.fall()
            if (jack.direction in ("right", "jleft")) and (not jack.jumping and not jack.falling):
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_left[0])
                game_canvas.itemconfig(jack.armor_img, image = jack.armor.images[1])
                if jack.direction == "right":
                    game_canvas.itemconfig(jack.weapon_img, image = jack.weapon.images[2])
                    game_canvas.move(jack.weapon_img, - 8, 0)
                jack.direction = "left"
                jack.step_cooldown = 9

            elif (jack.direction == "left" or jack.direction == "jright") and (jack.jumping or jack.falling):
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_left[3])
                game_canvas.itemconfig(jack.armor_img, image = jack.armor.images[1])
                if jack.direction == "jright":
                    game_canvas.itemconfig(jack.weapon_img, image = jack.weapon.images[2])
                    game_canvas.move(jack.weapon_img, - 8, 0)
                jack.direction = "jleft"

            jack.step_cooldown += 1

        if (jack.direction in ("jleft", "jright")) and (not jack.jumping and not jack.falling):
            if jack.direction == "jleft":
                jack.direction = "left"
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_left[0])
            elif jack.direction == "jright":
                jack.direction = "right"
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_right[0])


        if jack.step_cooldown == 10:
            jack.step_cooldown = 0
            if jack.direction == "right":
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_right[jack.next])

            elif jack.direction == "left":
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_left[jack.next])
            jack.next = 1 if jack.next == 2 else 2


        if not pressed["a"] and not pressed["d"] and not jack.jumping and not jack.falling:
            if jack.direction == "left":
                jack.direction = "left"
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_left[0])
            elif jack.direction == "right":
                jack.direction = "right"
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_right[0])
            jack.step_cooldown = 9

        if pressed["w"] and not jack.jumping:
            jack.jumping = True
            if jack.direction == "right":
                game_canvas.itemconfig(jack.character_img, image = postavy.MainCharacter.images_right[3])

        if jack.jumping or jack.falling:
            jack.jump()

        if jack.jumping and not bottom_check():
            jack.falling = True

        if jack.x >= 1280:
            jack.x = 10
            jack.y = 480
            jack.height = 0
            jack.offset = 0
            jack.max_offset = 200
            jack.jumping = False
            jack.falling = False
            if jack.hp <= 25:
                jack.hp += 5
            elif 25 < jack.hp:
                jack.hp = 30

            game_canvas.delete("map")

            if stage < 5:
                stage += 1
                load_level()

            elif stage == 5:
                stage = 1
                create_shop()

        if pressed["e"] or jack.attacking:
            if jack.attack_cooldown == 0:
                jack.attack(enemies)

        if jack.attack_cooldown > 0:
            jack.attack_cooldown -= 1

        for enemy in enemies:
            if enemy.alive:
                enemy.jackCheck(jack)
                if enemy.walking:
                    next_step = enemy.pattern.get()
                    if enemy.last_step != next_step:
                        if next_step == 1:
                            enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_right[0])
                            enemy.canvas.itemconfig(enemy.weapon_img, image = enemy.weapon.images[0])
                            enemy.step_count = 10
                            if enemy.direction == "left":
                                enemy.weapon_move = False
                                enemy.weapon_move_ = True
                            enemy.direction = "right"
                        elif next_step == -1:
                            enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_left[0])
                            enemy.canvas.itemconfig(enemy.weapon_img, image = enemy.weapon.images[2])
                            enemy.step_count = 10
                            if enemy.direction == "right":
                                enemy.weapon_move = True
                                enemy.weapon_move_ = True
                            enemy.direction = "left"
                        elif next_step == 0:
                            enemy.step_count = 0
                            if enemy.direction == "right":
                                enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_right[0])
                                enemy.canvas.itemconfig(enemy.weapon_img, image = enemy.weapon.images[0])
                            elif enemy.direction == "left":
                                enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_left[0])
                                enemy.canvas.itemconfig(enemy.weapon_img, image = enemy.weapon.images[2])

                    if enemy.step_count == 10:
                        if enemy.direction == "left":
                            if enemy.step == 1:
                                enemy.step = 2
                                enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_left[1])
                            elif enemy.step == 2:
                                enemy.step = 1
                                enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_left[2])
                        elif enemy.direction == "right":
                            if enemy.step == 1:
                                enemy.step = 2
                                enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_right[1])
                            elif enemy.step == 2:
                                enemy.step = 1
                                enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_right[2])
                        enemy.step_count = 0
                    enemy.last_step = next_step
                    if next_step != 0:
                        enemy.step_count += 1

                    enemy.move(next_step)
                    enemy.pattern.put(next_step)

                if not enemy.walking:
                    if enemy.direction == "left" and enemy.x - jack.x < 0:
                        enemy.direction = "right"
                        enemy.weapon_move = False
                        enemy.weapon_move_ = True
                        enemy.canvas.itemconfig(enemy.weapon_img, image = enemy.weapon.images[2])
                        enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_right[0])
                    elif enemy.direction == "right" and jack.x - enemy.x < 0:
                        enemy.direction = "left"
                        enemy.weapon_move = True
                        enemy.weapon_move_ = True
                        enemy.canvas.itemconfig(enemy.weapon_img, image = enemy.weapon.images[0])
                        enemy.canvas.itemconfig(enemy.character_img, image = enemy.images_left[0])

                if enemy.weapon_move and enemy.weapon_move_:
                    enemy.canvas.move(enemy.weapon_img, -8, 0)
                    enemy.weapon_move_ = False
                elif not enemy.weapon_move and enemy.weapon_move_:
                    enemy.canvas.move(enemy.weapon_img, 8, 0)
                    enemy.weapon_move_ = False


                if enemy.attack_cooldown == 0 or enemy.attacking:
                    enemy.attack(jack)

                try:
                    if enemy.move_l and not enemy.attacking:
                        enemy.canvas.move(enemy.character_img, 450, 0)
                        enemy.move_l = False
                except AttributeError:
                    pass


        if not jack.alive:
            if not end_bool:
                jack.x = 10
                jack.y = 480
                jack.height = 0
                jack.offset = 0
                jack.max_offset = 200
                jack.jumping = False
                jack.falling = False

                jack.hp = jack.player_data["parameters"]["hp"]

                main_game = False

                end_screen_f("death")

        try:
            if level == 4:
                if not enemies[0].alive:
                    if not end_bool:
                        end_screen_f("end")
                    end_bool = True
        except IndexError:
            pass

    game_canvas.after(25, main)



def end_screen_f(action):
    global end_screen_img, end_screen

    if action == "end":
        end_screen_img = tkinter.PhotoImage(file = "zdroje/images/end_screen/end.gif")
        end_screen = game_canvas.create_image(100, 100, image = end_screen_img, anchor = "nw")

        game_canvas.bind("<Return>", exit)

    else:
        end_screen_img = tkinter.PhotoImage(file = "zdroje/images/end_screen/end_2.gif")
        end_screen = game_canvas.create_image(100, 100, image = end_screen_img, anchor = "nw", tags = "end")

        game_canvas.bind("<Return>", restart)

    end_bool = False

## kontrola kolízie  --  kk

def right_check():
    end = True
    for side in level_data["level"]["obstacles"]:
        if (side[0] <= int(jack.x + 85)) and (side[0] >= int(jack.x + 80)) and (side[4][0] <= jack.offset < side[4][1]):
            end = False

    return end

def left_check():
    end = True
    for side in level_data["level"]["obstacles"]:
        if (side[2] <= int(jack.x + 5)) and (side[2] >= int(jack.x)) and (side[4][0] <= jack.offset < side[4][1]):
            end = False

    return end

def bottom_check():
    end = True
    for side in level_data["level"]["obstacles"]:
        if (side[4][0] == jack.offset) and (jack.x + 80 >= side[0]) and (jack.x <= side[2]):
            end = False

    return end




## inventárové funcie a jeho úprava  --  ifju

def create_inventory():
    global inventory_weapons, inventory_weapons_names, inventory_armors, inventory_armors_names, inventory_canvas, inventory_background, inventory_bg, inventory_img_armor, inventory_img_weapon

    inventory_bg = tkinter.PhotoImage(file = "zdroje/images/inventory/inventory.gif")
    inventory_background = inventory_canvas.create_image(0, 0, image = inventory_bg, anchor = "nw")


    inventory_weapons = []
    inventory_weapons_names = []
    inventory_armors = []
    inventory_armors_names = []

    # inventory_canvas.create_rectangle(3, 3, 1080, 520)
    y = 100
    for weapon in jack.weapons:

        inventory_weapons_names.append(weapon)
        inventory_weapons.append(inventory_canvas.create_rectangle(y - 1, 99, y + 101, 251, outline = "#f2e69b"))
        inventory_canvas.create_image(y + 10, 105, image = weapons[weapon].images[4], anchor = "nw")
        inventory_canvas.create_text(y + 5, 200, text = weapons[weapon].name, anchor = "nw")
        inventory_canvas.create_text(y + 5, 225, text = "Damage : {}".format(weapons[weapon].dmg), anchor = "nw")

        y += 125

    y = 100

    for armor in jack.armors:
        inventory_armors_names.append(armor)
        inventory_armors.append(inventory_canvas.create_rectangle(y - 1, 299, y + 101, 450, outline = "#f2e69b"))
        inventory_canvas.create_image(y + 7.5, 280, image = armors[armor].images[0], anchor = "nw")
        inventory_canvas.create_text(y + 5, 400, text = armors[armor].name, anchor = "nw")
        inventory_canvas.create_text(y + 5, 425, text = "Armor : {}".format(armors[armor].base_armor), anchor = "nw")

        y += 125

    inventory_canvas.create_image(820, 150, image = postavy.MainCharacter.images_right[4], anchor = "nw")
    inventory_img_armor = inventory_canvas.create_image(820, 150, image = jack.armor.images[2], anchor = "nw")
    inventory_img_weapon = inventory_canvas.create_image(820, 150, image = jack.weapon.images[5], anchor = "nw")

    inventory_canvas.place(x = 100, y = 100)




## Tvorba novej mapy  -- Tnm

def load_level():
    global level_data, jack, stage, level


    path_to_level = "zdroje/maps/level_{}_0{}.json".format(level, stage)

    with open(path_to_level) as f:
        level_data = json.load(f)

    jack.level_data = level_data

    jack.player_data["level_info"]["level"] = level
    jack.player_data["level_info"]["stage"] = stage
    jack.player_data["parameters"]["coins"] = jack.coins
    jack.player_data["parameters"]["hp"] = jack.hp
    # jack.player_data["armors"] = jack.armors
    # jack.player_data["weapons"] = jack.weapons
    with open("zdroje/saves/{}.json".format(save), "w") as f:
        json.dump(jack.player_data, f, indent = 2)

    create_map(level_data)


def create_map(level_data):
    global game_canvas, enemies, armor_x, jack, bg

    bg = tkinter.PhotoImage(file = "zdroje/images/level_background/level_{}.gif".format(level_data["level"]["level"]))
    background = game_canvas.create_image(0, 0, image = bg, anchor = "nw", tags = "map")
    enemies = []
    rectangle = []

    if level_data["level"]["level"] in (1, 2):
        color = "#2C1706"
    else:
        color = "#484343"


    for rectangle in level_data["level"]["obstacles"]:
        rectangle.append(game_canvas.create_rectangle(rectangle[:4], fill = color, outline = "black", width = 3, tags = "map"))

    for platform in level_data["level"]["platforms"]:
        if platform[1] != -100 and platform[2] != 1300:
            game_canvas.create_rectangle(platform[1], 600 - 180 * platform[0], platform[2], 620 - 180 * platform[0], fill = color, outline = "black", width = 3, tags = "map")

    for enemy in level_data["level"]["enemy_positions"]:
        if enemy[3] != "dragon":
            enemies.append(enemy_types[enemy[3]](enemy[1], 660 - 180 * (enemy[0] + 1), enemy[0], armor_x, weapons[enemy[3]], patterns.pattern[enemy[2]], game_canvas))
        else:
            enemies.append(enemy_types[enemy[3]](685, 160, 0, armor_x, weapons[enemy[3]], patterns.pattern[enemy[2]], game_canvas))


    [enemy.setAll() for enemy in enemies]


    jack.setAll()


def create_shop():
    global shop, level, shop_items, shop_bg, shop_bg_i, shop_coin, shop_coin_text, enemies

    enemies = list()

    shop_bg_i = tkinter.PhotoImage(file = "zdroje/images/inventory/shop.gif")

    shop_bg = game_canvas.create_image(0, 0, image = shop_bg_i, anchor = "nw", tags = "shop")

    shop_coin_text = game_canvas.create_text(1150, 25, text = "{}".format(jack.coins), tags = "shop")
    shop_coin = game_canvas.create_image(1180, 25, image = jack.coin, tags = "shop")

    for i in ((390, 0), (640, 1), (890, 2)):
        game_canvas.create_text(i[0], 430, text = shop_items[level][i[1]].name, tags = "shop")
        game_canvas.create_text(i[0], 450, text = shop_items[level][i[1]].price, tags = "shop")
        if shop_items[level][i[1]].is_armor:
            game_canvas.create_image(i[0], 320, image = shop_items[level][i[1]].images[0])
        elif not shop_items[level][i[1]].is_armor:
            game_canvas.create_image(i[0], 320, image = shop_items[level][i[1]].images[4])

    shop = True
    main_game = False

    level += 1



## Načítavanie postavy  --  np

def load_save(save):
    global player_data

    path_to_save = "zdroje/saves/{}.json".format(save)

    with open(path_to_save) as f:
        player_data = json.load(f)



## tvorba predmetov  --  tp

def createItems():
    global iron_sword, wolf_weapon, leather_armor, armor_x, weapons, armors, shop_items

    ## Zbrane

    iron_sword = predmety.Weapon("iron_sword", "Iron Sword", 5, 80, 1, 0, False, "iron_sword")
    steel_sword = predmety.Weapon("steel_sword", "Steel Sword", 7, 80, 1.5, 60, False, "steel_sword")
    dark_sword = predmety.Weapon("dark_sword", "Dark Sword", 15, 80, 3, 200, False, "dark_sword")
    golden_sword = predmety.Weapon("golden_sword", "Golden Sword", 12, 80, 2.5, 100, False, "golden_sword")

    dragonslayer = predmety.Weapon("dragonslayer" ,"Dragonslayer", 30, 100, 5, 300, False, "dragonslayer")

    wolf_weapon = predmety.Weapon("wolf", "Wolf", 5, 70, 0, 0, False, "iron_sword")
    super_wolf_weapon = predmety.Weapon("super_wolf", "Super Wolf", 10, 80, 0, 0, False, "iron_sword")

    dragon_weapon = predmety.Weapon("dragon", "Dragon", 10, 100, 0, 0, False, "dragonslayer")

    ## Zbroje

    leather_armor = predmety.Armor("leather_armor", "Leather Armor", 10, 0.5, 0, True, "leather_armor")
    steel_armor = predmety.Armor("steel_armor", "Steel Armor", 20, 1, 60, True, "steel_armor")
    black_armor = predmety.Armor("black_armor", "Black Armor", 40, 2, 150, True, "black_armor")
    golden_armor = predmety.Armor("golden_armor", "Golden Armor", 30, 1.5, 100, True, "golden_armor")

    dragon_armor = predmety.Armor("dragon_armor" ,"Dragon Armor", 60, 4, 300, True, "dragon_armor")

    armor_x = predmety.Armor("", "", 0, 0, 0, True, "leather_armor")

    weapons = {
    "iron_sword": iron_sword,
    "steel_sword": steel_sword,
    "dark_sword": dark_sword,
    "golden_sword": golden_sword,

    "dragonslayer": dragonslayer,

    "wolf": wolf_weapon,
    "goblin": iron_sword,
    "skeleton": steel_sword,

    "super_goblin": golden_sword,
    "super_skeleton": dark_sword,
    "super_wolf": super_wolf_weapon,

    "dragon": dragon_weapon
    }

    armors = {
    "leather_armor": leather_armor,
    "steel_armor": steel_armor,
    "black_armor": black_armor,
    "golden_armor": golden_armor,

    "dragon_armor": dragon_armor,

    "armor_x": armor_x
    }


    shop_items = {
        1: [steel_sword, steel_armor, black_armor],
        2: [golden_sword, golden_armor, dark_sword],
        3: [dragonslayer, dragon_armor, dragonslayer]
    }



def _pressed(event):
    if event.keysym != "i":
        pressed[event.keysym] = True


def _released(event):
    pressed[event.keysym] = False

def i_press(event):
    global main_game


    if main_game:
        create_inventory()
        main_game = False
    else:
        inventory_canvas.delete("all")
        inventory_canvas.place_forget()
        jack.setSpeed()
        game_canvas.delete("armor")
        jack.createArmors()
        main_game = True

        if jack.direction == "right" or jack.direction == "jright":
            game_canvas.itemconfig(jack.armor_img, image = jack.armor.images[0])
            game_canvas.itemconfig(jack.weapon_img, image = jack.weapon.images[0])
        else:
            game_canvas.itemconfig(jack.armor_img, image = jack.armor.images[1])
            game_canvas.itemconfig(jack.weapon_img, image = jack.weapon.images[2])

def inventory_click(event):
    for i in range(len(inventory_weapons)):
        item = inventory_canvas.coords(inventory_weapons[i])
        if event.x >= item[0] and event.x <= item[2] and event.y >= item[1] and event.y <= item[3]:
            jack.weapon = weapons[inventory_weapons_names[i]]
            jack.player_data["parameters"]["equiped_weapon"] = inventory_weapons_names[i]
            inventory_canvas.itemconfig(inventory_img_weapon, image = weapons[inventory_weapons_names[i]].images[5])


    for i in range(len(inventory_armors)):
        item = inventory_canvas.coords(inventory_armors[i])
        if event.x >= item[0] and event.x <= item[2] and event.y >= item[1] and event.y <= item[3]:
            jack.armor = armors[inventory_armors_names[i]]
            jack.player_data["parameters"]["equiped_armor"] = inventory_armors_names[i]
            inventory_canvas.itemconfig(inventory_img_armor, image = armors[inventory_armors_names[i]].images[2])

def shop_check(item):
    for i in jack.weapons.values():
        if i == item:
            return False
    for i in jack.armors.values():
        if i == item:
            return False

    return True

def shop_click(event):

    if shop:
        if 510 >= event.y >= 210:
            if 490 >= event.x >= 290:
                if shop_check(shop_items[level - 1][0]):
                    if jack.coins >= shop_items[level - 1][0].price:
                        jack.changeCoins(- shop_items[level - 1][0].price)
                        game_canvas.itemconfig(shop_coin_text, text = jack.coins)
                        if shop_items[level - 1][0].is_armor:
                            jack.armors[shop_items[level - 1][0]._name] = shop_items[level - 1][0]
                            jack.player_data["armors"].append(shop_items[level - 1][0]._name)
                        else:
                            jack.weapons[shop_items[level - 1][0]._name] = shop_items[level - 1][0]
                            jack.player_data["weapons"].append(shop_items[level - 1][0]._name)
            elif 740 >= event.x >= 540:
                if shop_check(shop_items[level - 1][1]):
                    if jack.coins >= shop_items[level - 1][1].price:
                        jack.changeCoins(- shop_items[level - 1][1].price)
                        game_canvas.itemconfig(shop_coin_text, text = jack.coins)
                        if shop_items[level - 1][1].is_armor:
                            jack.player_data["armors"].append(shop_items[level - 1][1]._name)
                            jack.armors[shop_items[level - 1][1]._name] = shop_items[level - 1][1]
                        else:
                            jack.weapons[shop_items[level - 1][1]._name] = shop_items[level - 1][1]
                            jack.player_data["weapons"].append(shop_items[level - 1][1]._name)
            elif 990 >= event.x >= 790:
                if shop_check(shop_items[level - 1][2]):
                    if jack.coins >= shop_items[level - 1][2].price:
                        jack.changeCoins(- shop_items[level - 1][2].price)
                        game_canvas.itemconfig(shop_coin_text, text = jack.coins)
                        if shop_items[level - 1][2].is_armor:
                            jack.armors[shop_items[level - 1][2]._name] = shop_items[level - 1][2]
                            jack.player_data["armors"].append(shop_items[level - 1][2]._name)
                        else:
                            jack.weapons[shop_items[level - 1][2]._name] = shop_items[level - 1][2]
                            jack.player_data["weapons"].append(shop_items[level - 1][2]._name)

    game_canvas.update()

def c_press(event):
    if shop and event.keysym == "c":
        game_canvas.delete("shop")
        jack.x = 10
        main_game = True
        load_level()

def arrow_move(event):
    global menu_pointer

    if event.keysym == "w" and menu_pointer > 0:
        menu_pointer -= 1
        game_canvas.move(arrow, 0, -150)
    elif event.keysym == "s" and menu_pointer < 2:
        menu_pointer += 1
        game_canvas.move(arrow, 0, 150)

def enter_game(event):
    global main_game, menu, new_game_bool, tutorial_img_1, tutorial_img_2, tutorial_bool, tutorial_bool_2, tutorial, menu_pointer

    try:
        if new_game_bool and not tutorial_bool:
            game_canvas.unbind("w")
            game_canvas.unbind("s")
            game_canvas.unbind("<Return>")
            menu = False
            main_game = True
            game_canvas.delete("all")
            load_game(str(menu_pointer + 1), True)  # keď bude fungovať tvorba hry False -> True
            main()
        elif not new_game_bool and not tutorial_bool:
            game_canvas.unbind("w")
            game_canvas.unbind("s")
            game_canvas.unbind("<Return>")
            menu = False
            main_game = True
            game_canvas.delete("all")
            load_game(str(menu_pointer + 1), False)  # keď bude fungovať tvorba hry False -> True
            main()

    except NameError:
        pass


    if menu and not tutorial_bool:

        if menu_pointer == 0:
            new_game_menu()
            new_game_bool = True
        elif menu_pointer == 1:
            new_game_menu()
            new_game_bool = False
        elif menu_pointer == 2:
            tutorial_img_1 = tkinter.PhotoImage(file = "zdroje/images/tutorial/tutorial_1.gif")
            tutorial_img_2 = tkinter.PhotoImage(file = "zdroje/images/tutorial/tutorial_2.gif")
            tutorial = game_canvas.create_image(640, 360, image = tutorial_img_1)
            tutorial_bool = True

    elif tutorial_bool:
        game_canvas.delete(tutorial)
        tutorial_bool = False


def restart(event):
    global end_screen, main_game, end_bool

    main_game = True
    jack.alive = True
    end_bool = False

    game_canvas.delete("end")
    game_canvas.unbind("<Return>")

    load_level()

## Tvorba hernej plochy  --  Thep

root.title("Jack")
root.geometry("1280x720+0+0")
game_canvas = tkinter.Canvas(root, width = 1280, height = 720)
game_canvas.pack()
game_canvas.focus_set()


## Tvorba inventára  --  tvi

inventory_canvas = tkinter.Canvas(root, width = 1080, height = 520)




## bind kláves a tlačidiel myši  --  bk

pressed = {}
for char in ("a", "d", "s", "w", "e", "i", "p", "f"):
    pressed[char] = False
game_canvas.bind("<KeyPress>", _pressed)
game_canvas.bind("<KeyRelease>", _released)
game_canvas.bind("i", i_press)
# game_canvas.bind("<Escape>", end_game)

game_canvas.bind("c", c_press)
game_canvas.bind("<Button-1>", shop_click)

inventory_canvas.bind("<Button-1>", inventory_click)

game_canvas.bind("w", arrow_move)
game_canvas.bind("s", arrow_move)
game_canvas.bind("<Return>", enter_game)


#### tvorba základných premenných a predmetov -- Tzp

enemy_types = {
"wolf": postavy.Wolf,
"goblin": postavy.Goblin,
"skeleton": postavy.Skeleton,

"super_wolf": postavy.SuperWolf,
"super_goblin": postavy.SuperGoblin,
"super_skeleton": postavy.SuperSkeleton,

"dragon": postavy.Dragon
}

createItems()





def load_game(save_num, new_game):
    global jack, jack_parameters, save, stage, level

    save = "save_{}".format(save_num)

    if new_game:
        load_save("save_new")
    else:
        load_save(save)

    jack_parameters = player_data["parameters"]

    level = player_data["level_info"]["level"]
    stage = player_data["level_info"]["stage"]

    jack_weapons = {n : weapons[n] for n in player_data["weapons"]}
    jack_armors = {n : armors[n] for n in player_data["armors"]}


    jack = postavy.MainCharacter(jack_parameters["start_x"], jack_parameters["start_y"], jack_parameters["start_height"], jack_parameters["base_health"], jack_parameters["hp"], jack_armors, jack_weapons, jack_parameters["equiped_armor"], jack_parameters["equiped_weapon"], jack_parameters["base_speed"], game_canvas, player_data)
    load_level()


def create_menu():
    global rect_img, arrow_img, arrow, menu_pointer, pointer_timer, bg, background, background_2, move_index, buttons, button_images, title_img

    bg = tkinter.PhotoImage(file = "zdroje/images/menu/menu_bg.gif")
    background = game_canvas.create_image(0, 0, image = bg, anchor = "nw")
    background_2 = game_canvas.create_image(1280, 0, image = bg, anchor = "nw")

    title_img = tkinter.PhotoImage(file = "zdroje/images/menu/title.gif")
    rect_img = tkinter.PhotoImage(file = "zdroje/images/menu/rect.gif")
    arrow_img = tkinter.PhotoImage(file = "zdroje/images/menu/arrow.gif")
    rect = []


    title = game_canvas.create_image(360, 360, image = title_img)
    arrow = game_canvas.create_image(680, 200, image = arrow_img, anchor = "nw", tags = "main_menu")

    menu_pointer = 0
    move_index = 0
    pointer_timer = 0

    button_images = []
    buttons = {}

    rect = []

    for i in (("new_game", 0, 200), ("load_game", 1, 350), ("tutorial", 2, 500)):
        button_images.append(tkinter.PhotoImage(file = "zdroje/images/menu/{}.gif".format(i[0])))
        buttons[i[0]] = button_images[i[1]]
        rect.append(game_canvas.create_image(800, i[2], image = buttons[i[0]], anchor = "nw"))


    start_game()

def start_game():
    global menu, main_game, pointer_timer, move_index, new_menu, tutorial_counter

    if menu or new_menu:

        if tutorial_bool:
            tutorial_counter += 1
            if tutorial_counter == 35:
                game_canvas.itemconfig(tutorial, image = tutorial_img_1)
            elif tutorial_counter == 70:
                game_canvas.itemconfig(tutorial, image = tutorial_img_2)
                tutorial_counter = 0


        game_canvas.move(background, -1, 0)
        game_canvas.move(background_2, -1, 0)
        move_index += 1

        if move_index == 1280:
            game_canvas.move(background, 2560, 0)
        elif move_index == 2560:
            game_canvas.move(background_2, 2560, 0)
            move_index = 0

        pointer_timer += 1

        if pointer_timer == 20:
            game_canvas.itemconfig(arrow, state = "hidden")
        elif pointer_timer == 25:
            game_canvas.itemconfig(arrow, state = "normal")
            pointer_timer = 0

        game_canvas.after(25, start_game)

def new_game_menu():
    global menu_pointer, menu, new_menu, arrow, buttons, button_images

    game_canvas.delete("main_menu")

    menu_pointer = 0
    new_menu = True
    menu = False

    arrow = game_canvas.create_image(680, 200, image = arrow_img, anchor = "nw")

    button_images = []
    buttons = {}

    for i in (("save_1", 0), ("save_2", 1), ("save_3", 2)):
        button_images.append(tkinter.PhotoImage(file = "zdroje/images/menu/{}.gif".format(i[0])))
        buttons[i[0]] = button_images[i[1]]

    rect = []

    for i in ((200, "save_1"), (350, "save_2"), (500, "save_3")):
        rect.append(game_canvas.create_image(800, i[0], image = buttons[i[1]], anchor = "nw"))


main_game = False
menu = True
shop = False
new_menu = False
tutorial_bool = False
end_bool = False
tutorial_counter = 0

## Spúšťanie main funkcie  --  Smf


if __name__ == "__main__":

    create_menu()

root.mainloop()
