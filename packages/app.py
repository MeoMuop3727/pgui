import pygame

pygame.init()

from pgui_module.components.scences import *
from pgui_module.systems.config import config
from pgui_module.components.ui import *

def App():
    config_screen = config()
    data = config_screen.load()

    config_screen.intro_doc(__name__)

    SIZE_SCREEN = (data["window"]["width"], data["window"]["height"])

    screen = pygame.display.set_mode(SIZE_SCREEN)
    pygame.display.set_caption(data["display"]["caption"])

    icon_game = pygame.image.load(data["display"]["icon"])
    pygame.display.set_icon(icon_game)

    manager = ManageScence(screen)

    class ScenceInit(Scence):
        def __init__(self, surface: pygame.Surface):
            super().__init__()

            self.__font = pygame.font.Font(None, 50)
            self.__content = data["display"]["caption"]
            self.__visible_text = False
            self.__time = 0.0
            self.__time_interval = 0.5
            self.__text = Label(
                surface,
                StyleLabel(
                    content=self.__content,
                    color="#ffffff",
                    bg_color="#000000",
                    pos=(
                        (surface.get_size()[0] - self.__font.size(self.__content)[0]) // 2 + 100,
                        surface.get_size()[1] // 2 + 200
                    ),
                    font=self.__font
                )
            )

            self.__logo = Image(
                surface,
                StyleImage(
                    path=data["display"]["icon"],
                    pos=(
                        (surface.get_size()[0] - self.__font.size(self.__content)[0]) // 2 + 50,
                        surface.get_size()[1] // 2 - 200
                    ),
                    mode="fit",
                    size=(300,300),
                    border_radius=500
                )
            )

        def render(self, screen):
            screen.fill("#000000")
            if self.__visible_text:
                self.__text.update()
            self.__logo.update()
        
        def update(self, dental):
            self.__time += dental
            if self.__time >= self.__time_interval:
                self.__visible_text = not self.__visible_text
                self.__time = 0.0

    manager.push_scence(ScenceInit(screen))

    manager.run() 