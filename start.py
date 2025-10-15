import pygame as p

p.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

PERS_WDT = 300
PERS_HGT = 375

FPS = 60

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

        self.load_animations()

        self.image = self.idle_anim_right[0]
        self.current_image = 0
        self.animations = self.idle_anim_right

        self.time = p.time.get_ticks()
        self.interval = 150

        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)

    def load_animations(self):
        self.idle_anim_right = []
        for i in range(1, 4):
            self.idle_anim_right.append(load_image(f"images/fire_wizard/idle{i}.png", PERS_WDT, PERS_HGT))

        self.idle_anim_left = []
        for image in self.idle_anim_right:
            self.idle_anim_left.append(p.transform.flip(image, True, False)) #true - вертикаль, false - горизонталь

    def update(self):
        if p.time.get_ticks() - self.time >= self.interval:
            self.current_image += 1
            if self.current_image >= len(self.animations):
                self.current_image = 0
                self.time = p.time.get_ticks()

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
        self.screen.blit(self.player.animations[self.player.current_image], self.player.rect)
        p.display.flip()


if __name__ == "__main__":
    Game()