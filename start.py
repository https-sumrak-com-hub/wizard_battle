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


class Player(p.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.key = None

        self.charge = False
        self.charge_power = 10
        self.image_charge_line = (p.Surface((self.charge_power, 10))).fill("red")

        self.anim_mode = "stay"
        self.side = "right"
        self.anim_type = f"{self.anim_mode}_{self.side}"

        self.wizard_type = "fire"  #may be lightning
        
        self.animations = self.load_animations()

        self.image_num = 0
        self.image = self.animations[self.anim_type][self.image_num]
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)
        self.time = p.time.get_ticks()
        self.interval = 480

    def charging(self):
        charge_image = load_image(f"images/{self.wizard_type}_wizard/charge.png", PERS_WDT, PERS_HGT)

        if self.key[K_SPACE]:
            self.charge = True

            if self.side == "left":
                self.image = p.image.transform.flip(charge_image, True, False)
            elif self.side == "right":
                self.image = charge_image





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

class Game:
    def __init__(self):

        # Создание окна
        self.screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        p.display.set_caption("Битва магов")
        p.display.set_caption("Wizard Battle")
        p.display.set_icon(load_image("images/icon.png", 10, 10))

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.player = Player()
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

        if self.player.charge:
            self.screen.blit(self.player.image_charge_line, self.player.rect_charge_line)

        p.display.flip()


if __name__ == "__main__":
    Game()