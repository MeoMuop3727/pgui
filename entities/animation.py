import pygame

class Animation:
    
    """Manage animation for sprite sheet"""

    def __init__(self, 
                 frames: list[pygame.Surface], 
                 fps: float = 12, 
                 loop: bool = True):
        self.frames = frames
        self.fps = fps
        self.loop = loop
        self.current_frame = 0
        self.timer = 0.0
        self.finished = False

    def update(self, dt: float):
        if self.finished: return

        self.timer += dt
        if self.timer >= 1.0 / self.fps:
            self.timer = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_frame(self) -> pygame.Surface:
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.timer = 0.0
        self.finished = False