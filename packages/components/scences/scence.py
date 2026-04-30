import pygame
from packages.systems.config import load_config_screen

__color_clear_frame = load_config_screen()["render"]["background-color"]

class Scence:

    """

    """

    def __init__(self) -> None:
        self.manager = None
    
    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, events: pygame.event.Event) -> None:
        pass
    
    def update(self, dental: float) -> None:
        pass
    
    def render(self, screen) -> None:
        screen.fill(__color_clear_frame) # Clear frame each after updating

# Just export Scence class
__all__ = ["Scence"]