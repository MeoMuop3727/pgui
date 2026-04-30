import pygame, sys
from .scence import Scence

class ManageScence:
    def __init__(self, screen: pygame.Surface):
        self.__screen = screen

        self.__scences: list[Scence] = []
        self.__running = True
        self.__clock = pygame.time.Clock()

    def push_scence(self, scence: Scence) -> None:
        scence.manager = self
        self.__scences.append(scence)
        scence.on_enter()

    def pop_scence(self) -> None:
        if self.__scences:
            scence = self.__scences.pop()
            scence.on_exit()
    
    def replace_scence(self, scence: Scence) -> None:
        self.pop_scence()
        self.push_scence(scence)
    
    def get_current_scence(self) -> Scence:
        return self.__scences[-1] if self.__scences else None
    
    def run(self, fps: int | float = 60) -> None:
        while self.__running:
            dt = self.__clock.tick(fps) / 1e3

            events = pygame.event.get()

            current_scence = self.get_current_scence()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if not current_scence: continue

            current_scence.handle_event(events)
            current_scence.update(dt)
            current_scence.render(self.__screen)

            pygame.display.flip()
            