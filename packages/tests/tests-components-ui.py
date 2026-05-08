import pygame

pygame.init()

from packages.components.scences import *
from packages.systems.config import load_config_screen
from packages.components.ui import *

config_screen = load_config_screen()

SIZE_SCREEN = (config_screen["window"]["width"], config_screen["window"]["height"])

screen = pygame.display.set_mode(SIZE_SCREEN)
pygame.display.set_caption(config_screen["display"]["caption"])

icon_game = pygame.image.load(config_screen["display"]["icon"])
pygame.display.set_icon(icon_game)

manager = ManageScence(screen)

def test_on_click():
    print("Clicked")

def draw_home(surface: pygame.Surface, offset):
    font = pygame.font.Font(None, 40)
    txt = font.render("HOME PAGE", True, "#000000")
    surface.blit(txt, (offset[0] + 100, -offset[1] + 100))

def draw_text(surface, offset):
    font = pygame.font.Font(None, 30)
    txt = font.render("TEST FUNC DRAW TEXT", True, "#000000")
    surface.blit(txt, (offset[0] + 100, -offset[1]))

class ScenceTest(Scence):
    def __init__(self, surface: pygame.Surface):
        super().__init__()

        self.s = ScrollView(surface, StyleScrollView(
            pos=(100,100),
            direction="vertical",
            size=(500,500),
            content_size=(1500,1500)
        ),
        draw_home)

    def render(self, screen):
        screen.fill("#ffffff")
        self.s.update()
    
    def handle_event(self, events):
        pass

manager.push_scence(ScenceTest(screen))

manager.run() # python3 -m packages.tests.tests-components-ui