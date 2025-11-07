import random
import screeninfo
import pygame as p
from pygame.constants import K_RCTRL, K_LCTRL, K_RALT, K_LALT

from start import SCREEN_WIDTH

p.init()

monitors = screeninfo.get_monitors()

SCREEN_WIDTH = monitors[0].width
SCREEN_HEIGHT = monitors[0].height


PERS_WDT = 300
PERS_HGT = 375

BUTTON_WIDTH = SCREEN_WIDTH/3
BUTTON_HEIGHT = SCREEN_WIDTH/20

FPS = 120

font = p.font.Font(None, 40)

def load_image(file, width, height):
    image = p.image.load(file).convert_alpha()
    image = p.transform.scale(image, (width, height))
    return image

def text_render(text, size=40, color="black"):
    return p.font.Font(None, int(size)).render(str(text), True, color)

class Fireball(p.sprite.Sprite):
    def __init__(self, coord, side, charge_power, way, screen):
        super().__init__()
        self.screen = screen

        self.side = side
        self.power = charge_power
        self.speed = 2 + self.power // 10  # чем больше заряд, тем быстрее летит
        self.fireball_images = {
            "l": load_image(f"{way}/ball.png", PERS_WDT / 3, PERS_HGT / 3)
        ,
            "r":  p.transform.flip(load_image(f"{way}/ball.png", PERS_WDT / 3, PERS_HGT / 3), True, False)

        }
        self.fireball_image = self.fireball_images[self.side]
        self.rect = self.fireball_image.get_rect()

        # позиция появления
        if self.side == "r":
            self.rect.center = (
                coord[0] + PERS_WDT - PERS_WDT // 4,
                coord[1] + PERS_HGT // 3
            )
        else:

            self.rect.center = (
                coord[0] + PERS_WDT // 4,
                coord[1] + PERS_HGT // 3
            )
        self.fireball_image = self.fireball_images[self.side]

    def move(self):
        if self.side == "r":
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

    def update(self):
        self.move()
        self.draw()

    def draw(self):
        self.screen.blit(self.fireball_image, self.rect)

    def offscreen(self):
        return self.rect.right < 0 or self.rect.left > SCREEN_WIDTH

class Personage(p.sprite.Sprite):
    def __init__(self, screen, player_number):
        super().__init__()
        self.screen = screen
        self.p_num = str(player_number)
        self.key = p.key.get_pressed()
        self.keys = {
            "1":[
                p.K_a, p.K_d, K_LCTRL, K_LALT
            ],
            "2":[
                p.K_LEFT, p.K_RIGHT, K_RCTRL, K_RALT
            ]
        }

        self.timer = p.time.get_ticks() + 600 #now time in milliseconds plus interval (for stay, walk and fireball delay attack) value

        with open("images/personages", "r") as file:
            self.wiz = (file.read()).split("\n")

        self.wiz = random.choice(self.wiz)

        self.charge_colors = {
            "afro": "red",
            "fire": "orange",
            "lightning": "blue"
        }

        self.way = f"images/{self.wiz}"

        self.anims = self.animations_storage()

        self.p_color = ""
        if self.p_num == "1":
            self.side = "r"
            self.p_color = "blue"
        else:
            self.side = "l"
            self.p_color = "red"

        self.move_type = "stay"
        self.img_mode = f"{self.move_type}_{self.side}"
        self.img_num = 0
        self.img = self.anims[self.img_mode][self.img_num]
        self.rect = self.img.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2) if self.p_num == "1" else (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)

        self.charge_mode = False
        self.charge_power = 1
        self.image_charge_line = p.Surface((self.charge_power, 10))
        self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT / 3, self.rect.topleft[1] + PERS_HGT / 5)

        self.name = text_render(f"{self.p_num} PLAYER", 50, self.p_color)
        self.name_rect = self.name.get_rect()

        self.min_hp = 10
        self.HEALTH = 100

        self.hp_line = p.Surface((self.HEALTH, 35))
        self.hp_line_coords = {
            "1": (20, 20),
            "2": (SCREEN_WIDTH - self.HEALTH - 20, 20)
        }
        self.hp_line_rect = self.hp_line.get_rect()
        self.hp_line_coord = (self.hp_line_coords[self.p_num])

        self.HEALTH_ = text_render(self.HEALTH, self.hp_line_rect[3] / 0.85, "black")

        self.fireballs = []

    def update(self):
        self.key = p.key.get_pressed()
        self.charging()
        self.move()

        self.HEALTH_ = text_render(self.HEALTH, self.hp_line_rect[3] / 0.85, "black")
        self.dead()
        #go to update fireballs
        for fireball in self.fireballs:
            fireball.update()

        #delete fireballs outside
        self.fireballs = [f for f in self.fireballs if not f.offscreen()]

    def new_img(self): #изменяет текущий номер изображения персонажа (при стоячем и ходячим положениях)
        curr_timer = p.time.get_ticks()
        if self.img_num < len(self.anims[self.img_mode]) - 1:
            if curr_timer > self.timer:
                self.img_num += 1
                self.timer = curr_timer + 600
        elif self.img_num >= len(self.anims[self.img_mode]) - 1:
            self.img_num = 0
            self.timer = curr_timer + 600
        self.img = self.anims[self.img_mode][self.img_num]

    def charging(self):
        curr_timer = p.time.get_ticks()
        if self.key[self.keys[self.p_num][3]] and curr_timer > self.timer and self.move_type == "super" and self.img_num == 1: #упростить условие
            self.charge_mode = True
            self.charge_power = min(self.charge_power + 1, 100)
            self.image_charge_line = p.Surface((self.charge_power, 10))
            self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT/3, self.rect.topleft[1] + 10)
            self.image_charge_line.fill(self.charge_colors[self.wiz])

        else:

            # если отпустил пробел после зарядки
            if self.charge_mode:
                new_ball = Fireball(self.rect.topleft, self.side, self.charge_power, self.way, self.screen)
                self.fireballs.append(new_ball)
                self.timer = curr_timer + 600
            self.charge_mode = False
            self.charge_power = 1

    def dead(self):
        if self.HEALTH == 0:
            self.img_mode = "dead"
            self.img_num = 0
            self.img = self.anims[self.img_mode][self.img_num]


    def move(self):
        if self.key[self.keys[self.p_num][0]] or self.key[self.keys[self.p_num][1]]:
            self.move_type = "move"

            if self.key[self.keys[self.p_num][0]]:
                self.side = "l"
                self.img_mode = f"{self.move_type}_{self.side}"
                self.new_img()
                if self.rect.left > 0:
                    self.rect.x -= 2.3

                else:
                    self.move_type = "stay"
                    self.img_num = 0
                    self.img_mode = f"{self.move_type}_{self.side}"
                    self.new_img()

            if self.key[self.keys[self.p_num][1]]:
                self.side = "r"
                self.img_mode = f"{self.move_type}_{self.side}"
                self.new_img()
                if self.rect.right < SCREEN_WIDTH:
                    self.rect.x += 2.3

                else:
                    self.move_type = "stay"
                    self.img_num = 0
                    self.img_mode = f"{self.move_type}_{self.side}"
                    self.new_img()

        elif self.key[self.keys[self.p_num][2]]:
            self.move_type = "super"
            self.img_num = 2 #sit image number in animations_storage
            self.img_mode = f"{self.move_type}_{self.side}"
            self.img = self.anims[self.img_mode][self.img_num]

        elif self.key[self.keys[self.p_num][3]]:
            self.move_type = "super"
            self.img_num = 1 #charging image number in self.anims[self.img_mode]
            self.img_mode = f"{self.move_type}_{self.side}"
            self.img = self.anims[self.img_mode][self.img_num]

        else:
            self.move_type = "stay"
            self.img_mode = f"{self.move_type}_{self.side}"
            self.new_img()

    def animations_storage(self):
        animation_images = {
            "stay_r":[
                load_image(f"{self.way}/stay{i}.png", PERS_WDT, PERS_HGT) for i in range(3)
            ],
            "stay_l":[
                p.transform.flip(load_image(f"{self.way}/stay{i}.png", PERS_WDT, PERS_HGT) , True, False) for i in range(3)
            ],
            "move_r":[
                load_image(f"{self.way}/move{i}.png", PERS_WDT, PERS_HGT) for i in range(4)
            ],
            "move_l":[
                p.transform.flip(load_image(f"{self.way}/move{i}.png", PERS_WDT, PERS_HGT), True, False) for i in range(4)
            ],
            "super_r":[
                load_image(f"{self.way}/attack.png", PERS_WDT, PERS_HGT),
                load_image(f"{self.way}/charge.png", PERS_WDT, PERS_HGT),
                load_image(f"{self.way}/sit.png", PERS_WDT, PERS_HGT)
            ],
            "super_l":[
                p.transform.flip(load_image(f"{self.way}/attack.png", PERS_WDT, PERS_HGT), True, False),
                p.transform.flip(load_image(f"{self.way}/charge.png", PERS_WDT, PERS_HGT), True, False),
                p.transform.flip(load_image(f"{self.way}/sit.png", PERS_WDT, PERS_HGT), True, False)
            ],
            "dead": [load_image("images/empty.png", 1, 1)]
        }

        return animation_images

class Game:
    def __init__(self, mode):
        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        p.display.set_caption("BATTLE")
        p.display.set_icon(load_image("images/icon.png", 10, 10))
        self.mode = mode

        self.locations = [
            load_image(f"images/location{i}.png", SCREEN_WIDTH, SCREEN_HEIGHT) for i in range(3)
        ]

        self.wall_negative = load_image("images/wall_negative.png", SCREEN_WIDTH, 100)
        self.background = random.choice(self.locations)
        self.player1 = Personage(self.screen, 1)
        self.player2 = Personage(self.screen, 2)

        self.clock = p.time.Clock()
        if self.mode == "game":
            self.run()

        else:
            MainMenu()

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in p.event.get():
            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    self.mode = "main"
                    MainMenu()

    def update(self):
        #go to update current players
        self.player1.update()
        self.player2.update()
        if self.player1.fireballs or self.player2.fireballs:
            self.UNHEALWITHFIREBALLS()

    def UNHEALWITHFIREBALLS(self):
        for fireball in self.player1.fireballs:
            if self.player2.img_mode != "dead" and self.player2.move_type != "super" and self.player2.img_num != 2:
                if p.sprite.spritecollide(fireball, [self.player2], False, p.sprite.collide_rect_ratio(0.6)):
                    if self.player2.HEALTH - fireball.power // 5  > 0:
                        self.player2.HEALTH -= fireball.power // 5
                    else:
                        self.player2.HEALTH = 0

                    self.player1.fireballs.remove(fireball)
                
        for fireball in self.player2.fireballs:
            if self.player1.img_mode != "dead" and self.player1.move_type != "super" and self.player1.img_num != 2:
                if p.sprite.spritecollide(fireball, [self.player1], False, p.sprite.collide_rect_ratio(0.6)):
                    if self.player1.HEALTH - fireball.power // 5 > 0:
                        self.player1.HEALTH -= fireball.power // 5
                    else:
                        self.player1.HEALTH = 0

                    self.player2.fireballs.remove(fireball)

    def draw(self):
        self.screen.blit(self.background, (0, 0))

        # blit current players
        self.screen.blit(self.player1.img, self.player1.rect)
        self.screen.blit(self.player2.img, self.player2.rect)

        if self.player1.charge_mode:
           self.screen.blit(self.player1.image_charge_line, self.player1.rect_charge_line)

        if self.player2.charge_mode:
            self.screen.blit(self.player2.image_charge_line, self.player2.rect_charge_line)

        self.screen.blit(self.wall_negative, (0, 0))

        if self.player1.HEALTH > self.player1.min_hp:
            self.player1.hp_line.fill("green")
        else:
            self.player1.hp_line.fill("red")

        self.screen.blit(self.player1.hp_line, self.player1.hp_line_coord)
        self.screen.blit(self.player1.HEALTH_, self.player1.hp_line_coord)
        self.screen.blit(self.player1.name, (SCREEN_WIDTH//2 - self.player1.name_rect[2]*2, 20))

        if self.player2.HEALTH > self.player2.min_hp:
            self.player2.hp_line.fill("green")
        else:
            self.player2.hp_line.fill("red")

        self.screen.blit(self.player2.hp_line, self.player2.hp_line_coord)
        self.screen.blit(self.player2.HEALTH_, self.player2.hp_line_coord)
        self.screen.blit(self.player2.name, (SCREEN_WIDTH//2 + self.player2.name_rect[2], 20))

        #blit current fireballs
        for fireball in self.player1.fireballs:
            fireball.draw()

        for fireball in self.player2.fireballs:
            fireball.draw()

        if self.player1.HEALTH == 0:
            self.mode = "menu"
            self.screen.blit(text_render("2 PLAYER WINS!", SCREEN_WIDTH // 25, "red"), (SCREEN_WIDTH / 2 - SCREEN_WIDTH // 25 * 2.5, SCREEN_HEIGHT / 2))



        if self.player2.HEALTH == 0:
            self.mode = "menu"
            self.screen.blit(text_render("1 PLAYER WINS!", SCREEN_WIDTH // 25, "blue"), (SCREEN_WIDTH / 2 - SCREEN_WIDTH // 25 * 2.5, SCREEN_HEIGHT / 2))


        p.display.flip()

class Button:
    def __init__(self, text, x, y, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=font, func=None, button="wall", button_clicked="wall_negative"):
        self.func = func

        try:
            self.idle_image = load_image(f"images/{button}.png", width, height)
            self.pressed_image = load_image(f"images/{button_clicked}.png", width, height)
        except:
            self.idle_image = button
            self.pressed_image = button_clicked

        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.text_font = text_font
        self.text = {
            "unclicked": self.text_font.render(str(text), True, "white"),
            "clicked": self.text_font.render(str(text), True, "black")
        }
        self.text_mode = "unclicked"
        self.text_rect = self.text[self.text_mode].get_rect()
        self.text_rect.center = self.rect.center

        self.is_pressed = False

    def update(self):
        self.is_touched()

    def is_touched(self):
        mouse_position = p.mouse.get_pos()
        if self.rect.collidepoint(mouse_position):
            self.image = self.pressed_image
            self.text_mode = "clicked"
        else:
            self.image = self.idle_image
            self.text_mode = "unclicked"

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text[self.text_mode], self.text_rect)

class Settings:
    def __init__(self, mode):
        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        p.display.set_caption("SETTINGS")
        p.display.set_icon(load_image("images/icon.png", 10, 10))

        self.settings_text = text_render("НАСТРОЙКИ", SCREEN_HEIGHT//10, "white")
        self.settings_text_rect = self.settings_text.get_rect()

        self.mode = mode
        self.full = (monitors[0].width, monitors[0].height)
        self.s1280 = (1280, 1024)
        self.s1080 = (1080, 1080)
        self.background = load_image("images/wall.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.buttons = [
            Button("Полноэкранное", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                   text_font=p.font.Font(None, SCREEN_HEIGHT//30), func=lambda: self.set_up(self.full)),
            Button("1280x1024", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + BUTTON_HEIGHT * 1.5,
                   width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=p.font.Font(None, SCREEN_HEIGHT//30), func=lambda: self.set_up(self.s1280)),
            Button("1080x1080", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + BUTTON_HEIGHT * 3,
                   width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=p.font.Font(None, SCREEN_HEIGHT // 30),
                   func=lambda: self.set_up(self.s1080))
        ]

        self.clock = p.time.Clock()

        if self.mode == "settings":
            self.run()
        else:
            MainMenu()


    def run(self):
        while True:
            self.draw()
            self.update()
            self.clock.tick(FPS)

    def set_up(self, MODE):
        global SCREEN_WIDTH, SCREEN_HEIGHT
        if MODE == self.full:
            SCREEN_WIDTH = self.full[0]
            SCREEN_HEIGHT = self.full[1]

        elif MODE == self.s1280:
            SCREEN_WIDTH = self.s1280[0]
            SCREEN_HEIGHT = self.s1280[1]

        elif MODE == self.s1080:
            SCREEN_WIDTH = self.s1080[0]
            SCREEN_HEIGHT = self.s1080[1]

        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.mode = "main"

    def update(self):
        self.event()
        if self.mode == "main":
            MainMenu()
        for button in self.buttons:
            button.update()

    def event(self):
        for event in p.event.get():
            if event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    self.mode = "main"

            for button in self.buttons:
                if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                    if button.rect.collidepoint(event.pos):
                        button.func()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.settings_text, (SCREEN_WIDTH / 2 - self.settings_text_rect[2] / 2, SCREEN_HEIGHT / 5))

        for button in self.buttons:
            button.draw(self.screen)

        p.display.flip()

class MainMenu:
    def __init__(self):
        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        p.display.set_caption("Wizard Battle (ver. 1)")
        p.display.set_icon(load_image("images/icon.png", 10, 10))

        self.mode = "menu"
        self.game = None
        self.settings = None

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.icon = load_image("images/icon.png", 200, 200)
        self.icon_rect = self.icon.get_rect()
        self.icon_rect.center = (SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/20)

        self.buttons = [
            Button("ИГРАТЬ", SCREEN_WIDTH/2, SCREEN_HEIGHT/2, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=p.font.Font(None, SCREEN_HEIGHT//30), func=self.start),
            Button("НАСТРОЙКИ", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + BUTTON_HEIGHT*1.5, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=p.font.Font(None, SCREEN_HEIGHT//30), func=self.settings_start),
            Button("ВЫХОД", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + BUTTON_HEIGHT*3, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=p.font.Font(None, SCREEN_HEIGHT//30), func=self.quit)
        ]

        self.clock = p.time.Clock()
        self.run()

    def run(self):
        while True:
            self.update()
            self.draw()

    def start(self):
        self.mode = "game"
        self.game = Game(self.mode)

    def settings_start(self):
        self.mode = "settings"
        self.settings = Settings(self.mode)

    def quit(self):
        quit()

    def event(self):
        for event in p.event.get():
            if event.type == p.QUIT:
                quit()
            for button in self.buttons:
                if event.type == p.MOUSEBUTTONDOWN and event.button == 1:
                    if button.rect.collidepoint(event.pos):
                        button.func()


    def update(self):
        self.event()
        for button in self.buttons:
            button.update()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.icon, self.icon_rect.center)

        for button in self.buttons:
            button.draw(self.screen)

        p.display.flip()

MainMenu()