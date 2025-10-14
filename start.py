import pygame as pg

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

FPS = 60

font = pg.font.Font(None, 40)


def load_image(file, width, height):
    image = pg.image.load(file).convert_alpha()
    image = pg.transform.scale(image, (width, height))
    return image


def text_render(text):
    return font.render(str(text), True, "black")


class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = 0 #refactor

        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT // 2)


class Game:
    def __init__(self):

        # Создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Битва магов")
        window_icon = pg.Surface().icon()

        self.background = load_image("images/background.png", SCREEN_WIDTH, SCREEN_HEIGHT)

        self.clock = pg.time.Clock()
        self.run()

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                quit()

    def update(self):
        pass

    def draw(self):
        # Отрисовка интерфейса
        self.screen.blit(self.background, (0, 0))

        pg.display.flip()


if __name__ == "__main__":
    Game()