import pygame

pygame.init()

from packages.components.scences import *
from packages.systems.config import load_config_screen, intro_doc

def TestsComponentsScence():
    config_screen = load_config_screen()

    intro_doc(__name__)    

    SIZE_SCREEN = (config_screen["window"]["width"], config_screen["window"]["height"])

    screen = pygame.display.set_mode(SIZE_SCREEN)
    pygame.display.set_caption(config_screen["display"]["caption"])

    icon_game = pygame.image.load(config_screen["display"]["icon"])
    pygame.display.set_icon(icon_game)

    manager = ManageScence(screen)

    class ScenceInit(Scence):
        def __init__(self, surface: pygame.Surface):
            super().__init__()

            # Create in here

        def render(self, screen):
            screen.fill("#000000")

    manager.push_scence(ScenceInit(screen))

    manager.run() 