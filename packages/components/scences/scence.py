import pygame
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
    
    def render(self, screen: pygame.Surface) -> None:
        pass

# Just export Scence class
__all__ = ["Scence"]