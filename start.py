import pygame as p
from pygame.constants import K_DOWN, K_LCTRL, K_SPACE

p.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

PERS_WDT = 300
PERS_HGT = 375

FPS = 24

font = p.font.Font(None, 40)


def load_image(file, width, height):
    image = p.image.load(file).convert_alpha()
    image = p.transform.scale(image, (width, height))
    return image


def text_render(text):
    return font.render(str(text), True, "black")

class Fireball:
    def __init__(self, coord, side, charge_power, wizard_type, screen):
        self.screen = screen

        self.player_coords = coord
        self.side = side
        self.power = charge_power
        self.fireball_image = load_image(f"images/{wizard_type}_wizard/{wizard_type}_ball.png", PERS_WDT, PERS_HGT)
        self.fireball_rect = self.fireball_image.get_rect()


    def move(self):
        pass

    def update(self):
        self.draw()

    def draw(self):
        if self.power == 100:
            # if self.side == "right":
            #     self.fireball_rect.center = (self.player_coords[0] + PERS_WDT, self.player_coords[1] - PERS_HGT/2)
            # else:
            #     self.fireball_rect.center = (self.player_coords[0], self.player_coords[1] - PERS_HGT / 2)

            self.screen.blit(self.fireball_image, self.fireball_rect.center)


class Player(p.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen

        self.anim_mode = "stay"
        self.side = "right"
        self.anim_type = f"{self.anim_mode}_{self.side}"

        self.wizard_type = "fire"

        self.animations = self.load_animations()

        self.image_num = 0
        self.image = self.animations[self.anim_type][self.image_num]
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.time = p.time.get_ticks()
        self.interval = 480

        # Заряд


        # Список активных фаерболов
        self.fireballs = []

    def charging(self):
        """Режим зарядки — удержание пробела."""
        " Добавить таймер для выстрела "
        if self.key[K_SPACE] and p.time.get_ticks() - self.time > 23:
            self.charge_mode = True
        else:

            # если отпустил пробел после зарядки
            if self.charge_mode and self.charge_power > 1:
                new_ball = Fireball(self.rect.topleft, self.side, self.charge_power, self.wizard_type, self.screen)
                self.fireballs.append(new_ball)
                self.anim_mode = "attack"
            self.charge_mode = False
            self.charge_power = 1

        self.animation_choice()

    def movement_checker(self):
        if self.key[p.K_a] or self.key[p.K_d]:
            self.anim_mode = "move"

            if self.key[p.K_a]:
                if self.rect.left > 0:
                    self.side = "left"
                    self.rect.x -= 10

            if self.key[p.K_d]:
                if self.rect.right < SCREEN_WIDTH:
                    self.side = "right"
                    self.rect.x += 10

        elif self.key[K_LCTRL]:
            self.anim_mode = "super"

        else:
            self.anim_mode = "stay"

        self.animation_choice()

    def load_animations(self):
        idle_animations = {
            "stay_right": [load_image(f"images/{self.wizard_type}_wizard/idle{i}.png", PERS_WDT, PERS_HGT) for i in
                           range(1, 4)],
            "stay_left": [
                p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/idle{i}.png", PERS_WDT, PERS_HGT), True,
                                 False) for i in range(1, 4)],
            "move_right": [load_image(f"images/{self.wizard_type}_wizard/move{i}.png", PERS_WDT, PERS_HGT) for i in
                           range(1, 5)],
            "move_left": [
                p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/move{i}.png", PERS_WDT, PERS_HGT), True,
                                 False) for i in range(1, 5)],
            "super_right": [
                load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT),
                load_image(f"images/{self.wizard_type}_wizard/down.png", PERS_WDT, PERS_HGT)
            ],
            "super_left": [
                p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT), True,
                                 False),
                p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/down.png", PERS_WDT, PERS_HGT), True,
                                 False)
            ],
            "attack_right": load_image(f"images/{self.wizard_type}_wizard/attack.png", PERS_WDT, PERS_HGT)
            ,
            "attack_left": p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/attack.png", PERS_WDT, PERS_HGT), True,
                                 False)
        }
        return idle_animations

    def update(self):
        self.key = p.key.get_pressed()
        self.charging()
        self.movement_checker()

        # обновляем фаерболы
        for fireball in self.fireballs:
            fireball.update()

        # удаляем те, что улетели
        self.fireballs = [f for f in self.fireballs if not f.offscreen()]

    def animation_choice(self):
        current_time = p.time.get_ticks()

        if self.anim_mode in ["stay", "move"]:
            self.anim_type = f"{self.anim_mode}_{self.side}"

            if self.image_num == len(self.animations[self.anim_type]):
                self.image_num = 0

            if current_time - self.time >= self.interval:
                self.image_num = (self.image_num + 1) % len(self.animations[self.anim_type])
                self.time = current_time

            self.image = self.animations[self.anim_type][self.image_num]

        if self.anim_mode == "super":
            self.anim_type = f"{self.anim_mode}_{self.side}"
            self.image_num = 1
            self.image = self.animations[self.anim_type][self.image_num]

        if self.anim_mode == "attack":
            self.anim_type = f"{self.anim_mode}_{self.side}"
            self.image = self.animations[self.anim_type]

        # Зарядка
        if self.charge_mode:
            self.charge_power = min(self.charge_power + 2, 100)
            self.image = self.charge_image[0] if self.side == "right" else self.charge_image[1]
            self.image_charge_line = p.Surface((self.charge_power, 10))
            self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT / 3, self.rect.topleft[1] + 10)
            self.image_charge_line.fill("red")



class Enemy(p.sprite.Sprite):
    def __init__(self, screen, player):
        super().__init__()
        self.screen = screen
        self.player = player

        self.anim_mode = "stay"
        self.side = "left"
        self.anim_type = f"{self.anim_mode}_{self.side}"

        self.wizard_type = random.choice(["afro", "lightning"]) #may be lightning and afro

        self.animations = self.load_animations()

        self.image_num = 0
        self.image = self.animations[self.anim_type][self.image_num]
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)
        self.time = p.time.get_ticks()
        self.interval = 480

        self.charge_mode = False
        self.charge_power = 1
        self.image_charge_line = p.Surface((self.charge_power, 10))
        self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT / 3, self.rect.topleft[1] + PERS_HGT / 10)
        self.charge_image = [
                             load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT),
                             p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT), True, False)
                            ]

        self.fireballs = []

    def update(self):
        self.key = p.key.get_pressed()
        self.charging()
        self.movement_choice()

        for fireball in self.fireballs:
            fireball.update()
        self.fireballs = [f for f in self.fireballs if not f.offscreen()]

    def load_animations(self):
        idle_animations = {
            "stay_right": [ load_image(f"images/{self.wizard_type}_wizard/idle{i}.png", PERS_WDT, PERS_HGT) for i in range(1, 4)],
            "stay_left": [  p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/idle{i}.png", PERS_WDT, PERS_HGT), True, False) for i in range(1, 4)],
            "move_right": [ load_image(f"images/{self.wizard_type}_wizard/move{i}.png", PERS_WDT, PERS_HGT) for i in range(1, 5)],
            "move_left": [  p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/move{i}.png", PERS_WDT, PERS_HGT), True, False) for i in range(1, 5)],
            "super_right": [
                            load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT),
                            load_image(f"images/{self.wizard_type}_wizard/down.png", PERS_WDT, PERS_HGT)
                           ],
            "super_left": [
                            p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT), True, False),
                            p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/down.png", PERS_WDT, PERS_HGT), True, False)
                          ],
            "attack_right": load_image(f"images/{self.wizard_type}_wizard/attack.png", PERS_WDT, PERS_HGT)
                          ,
            "attack_left": p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/attack.png", PERS_WDT, PERS_HGT), True, False)

        }
        return idle_animations

    def charging(self):
        """Режим зарядки — удержание пробела."""
        " Добавить таймер для выстрела "
        if p.time.get_ticks() - self.time > 2:
            self.charge_mode = True
        else:
            if self.charge_mode and self.charge_power > 1:
                self.anim_mode = "attack"
                new_ball = Fireball(self.rect.topleft, self.side, self.charge_power, self.wizard_type, self.screen)
                self.fireballs.append(new_ball)
            self.charge_mode = False
            self.charge_power = 1
        self.animation_choice()

    # def movement_checker(self):
    #     if self.key[p.K_a] or self.key[p.K_d]:
    #         self.anim_mode = "move"
    #
    #         if self.key[p.K_a]:
    #             if self.rect.left > 0:
    #                 self.side = "left"
    #                 self.rect.x -= 10
    #
    #         if self.key[p.K_d]:
    #             if self.rect.right < SCREEN_WIDTH:
    #                 self.side = "right"
    #                 self.rect.x += 10
    #
    #     elif self.key[K_LCTRL]:
    #         self.anim_mode = "super"
    #
    #     else:
    #         self.anim_mode = "stay"
    #
    #     self.animation_choice()


    def movement_choice(self):
        if self.player.anim_mode in ["stay", "move"]:
            self.charging()




    def animation_choice(self):
        current_time = p.time.get_ticks()

        if self.anim_mode in ["stay", "move"]:
            self.anim_type = f"{self.anim_mode}_{self.side}"

            if self.image_num == len(self.animations[self.anim_type]):
                self.image_num = 0

            if current_time - self.time >= self.interval:
                self.image_num = (self.image_num + 1) % len(self.animations[self.anim_type])
                self.time = current_time

            self.image = self.animations[self.anim_type][self.image_num]

        if self.anim_mode == "super":
            self.anim_type = f"{self.anim_mode}_{self.side}"
            self.image_num = 1
            self.image = self.animations[self.anim_type][self.image_num]

        if self.anim_mode == "attack":
            self.anim_type = f"{self.anim_mode}_{self.side}"
            self.image = self.animations[self.anim_type]

        # Зарядка
        if self.charge_mode:
            self.charge_power = min(self.charge_power + 2, 100)
            self.image = self.charge_image[0] if self.side == "right" else self.charge_image[1]
            self.image_charge_line = p.Surface((self.charge_power, 10))
            self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT / 3, self.rect.topleft[1] + 10)
            self.image_charge_line.fill("red")


class Player(p.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.key = None

        self.anim_mode = "stay"
        self.side = "right"
        self.anim_type = f"{self.anim_mode}_{self.side}"

        self.wizard_type = "fire"  #may be lightning and afro
        
        self.animations = self.load_animations()

        self.image_num = 0
        self.image = self.animations[self.anim_type][self.image_num]
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.time = p.time.get_ticks()
        self.interval = 480

        self.charge_mode = False
        self.charge_power = 1
        self.image_charge_line = p.Surface((self.charge_power, 10))
        self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT/3, self.rect.topleft[1] + PERS_HGT/10)
        self.charge_image = [load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT), p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT), True, False)]
        self.fireball = Fireball(self.rect.topleft, self.side, self.charge_power, self.wizard_type, screen)
        Fireball.__init__(self, self.rect.topleft, self.side, self.charge_power, self.wizard_type, screen)

    def charging(self):
        if self.key[K_SPACE]:
            self.charge_mode = True
        else:
            self.charge_mode = False

        self.animation_choice()

    def movement_checker(self):
        if self.key[p.K_a] or self.key[p.K_d]:
            self.anim_mode = "move"

            if self.key[p.K_a]:
                if 0 <= self.rect.bottomleft[0] <= SCREEN_WIDTH:
                    self.side = "left"
                    self.rect[0] -= 10
                else:
                    self.image_num = 0
                    self.anim_mode = "stay"

            if self.key[p.K_d]:
                if 0 <= self.rect.bottomright[0] <= SCREEN_WIDTH:
                    self.side = "right"
                    self.rect[0] += 10
                else:
                    self.image_num = 0
                    self.anim_mode = "stay"

        elif self.key[K_LCTRL]:
            self.anim_mode = "super"

        elif self.anim_mode == "stay" and self.key[p.K_a] == False and self.key[p.K_d] == False:
            self.anim_mode = "stay"

        else:
            self.image_num = 0
            self.anim_mode = "stay"

        self.animation_choice()



        # for event in p.event.get():
        #     if event.type == p.KEYDOWN:
        #         if event.key == p.K_a or event.key == p.K_d:
        #             self.anim_mode = "move"
        #
        #             if event.key == p.K_a:
        #                 if 0 <= self.rect.bottomleft[0] <= SCREEN_WIDTH:
        #                      = "a"
        #                     self.animation_choice()
        #                     self.rect[0] -= 10
        #
        #             if event.key == p.K_d:
        #                 if 0 <= self.rect.bottomright[0] <= SCREEN_WIDTH:
        #                      = "d"
        #                     self.animation_choice()
        #                     self.rect[0] += 10
        #
        #         if event.key == p.K_LCTRL:
        #             self.anim_mode = "super"
        #
        #             if event.key == p.K_LCTRL:
        #                  = "lctrl"
        #                 self.animation_choice()
        #
        #     if event.type == p.KEYUP:
        #         if event.key == p.L_CTRL: #возможно добавление новых клавиш управления
        #             self.anim_mode = "super"
        #
        #             if event.key == p.K_LCTRL:
        #                  = None
        #                 self.animation_choice()
        #
        #     if event.type != p.KEYDOWN and event.type != p.KEYUP:
        #         self.anim_mode = "stay"
        #          = None
        #         self.animation_choice()

    def load_animations(self):
        idle_animations = {
            "stay_right": [load_image(f"images/{self.wizard_type}_wizard/idle{i}.png", PERS_WDT, PERS_HGT) for i in range(1, 4)],

            "stay_left": [p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/idle{i}.png", PERS_WDT, PERS_HGT), True, False) for i in range(1, 4)], # true - вертикаль, false - горизонталь

            "move_right": [load_image(f"images/{self.wizard_type}_wizard/move{i}.png", PERS_WDT, PERS_HGT) for i in range(1, 5)],

            "move_left": [p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/move{i}.png", PERS_WDT, PERS_HGT), True, False) for i in range(1, 5)], # true - вертикаль, false - горизонталь

            "super_right": [
                                      load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT),
                                      load_image(f"images/{self.wizard_type}_wizard/down.png", PERS_WDT, PERS_HGT)
                           ],

            "super_left": [
                                     p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT), True, False),
                                     p.transform.flip(load_image(f"images/{self.wizard_type}_wizard/down.png", PERS_WDT, PERS_HGT), True, False)
                          ]
        }

        return idle_animations

    def update(self):
        self.key = p.key.get_pressed()
        self.charging()
        self.fireball.update()
        self.movement_checker()


    def animation_choice(self):
        if self.anim_mode == "stay":
            self.anim_type = f"{self.anim_mode}_{self.side}"

            current_time = p.time.get_ticks()

            if current_time - self.time >= self.interval:
                self.image_num += 1
                if self.image_num == len(self.animations[self.anim_type]):
                    self.image_num = 0
                self.time = current_time

            self.image = self.animations[self.anim_type][self.image_num]

        if self.anim_mode == "move":
            self.anim_type = f"{self.anim_mode}_{self.side}"

            current_time = p.time.get_ticks()

            if current_time - self.time >= self.interval:
                self.image_num += 1
                if self.image_num == len(self.animations[self.anim_type]):
                    self.image_num = 0
                self.time = current_time

            self.image = self.animations[self.anim_type][self.image_num]

            # if  == "d":
            #     self.side = "right"
            #     self.anim_type = f"{self.anim_mode}_{self.side}"
            #
            #     self.time = p.time.get_ticks()
            #
            #     if p.time.get_ticks() - self.time >= self.interval:
            #         self.image_num += 1
            #         if self.image_num >= len(self.animations[self.anim_type]):
            #             self.image_num = 0
            #         self.update()
            #         self.time = p.time.get_ticks()
            #
            #         self.image = self.animations[self.anim_type][self.image_num]

        if self.anim_mode == "super":
            self.anim_type = f"{self.anim_mode}_{self.side}"

            self.image_num = 1 #индекс сидячего положения в моде super списка super_right/left словаря animations

            self.image = self.animations[self.anim_type][self.image_num]

            # В дальнейшем добавить передвижение в сидячем состоянии ->
            #
            # keys = p.key.get_pressed()
            # for key in keys:
            #     if key[K_LCTRL]:
            #         self.image_num = 0
            #         self.update()

        if self.charge_mode:
            if self.charge_power >= 100:
                self.charge_mode = False
                self.charge_power = 0
            else:
                self.charge_power += 10

            if self.side == "right":
                self.image = self.charge_image[0]
            else:
                self.image = self.charge_image[1]

            self.image_charge_line = p.Surface((self.charge_power, 10))
            self.rect_charge_line = (self.rect.topleft[0] + PERS_WDT / 3, self.rect.topleft[1] + 10)
            self.image_charge_line.fill("red")

class Game:
    def __init__(self):

        # Создание окна
        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        p.display.set_caption("Битва магов")
        p.display.set_caption("Wizard Battle")
        p.display.set_icon(load_image("images/icon.png", 10, 10))

        self.background = load_image("images/location0.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.player = Player(self.screen)
        self.clock = p.time.Clock()
        self.run()

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in p.event.get():
            if event.type == p.QUIT:
                quit()

    def update(self):
        self.player.update()

    def draw(self):
        # Отрисовка интерфейса
        self.screen.blit(self.background, (0, 0))
        #self.player.anim_mode = True
        self.screen.blit(self.player.image, self.player.rect)

        if self.player.charge_mode:
            self.screen.blit(self.player.image_charge_line, self.player.rect_charge_line)

        p.display.flip()


if __name__ == "__main__":
    Game()