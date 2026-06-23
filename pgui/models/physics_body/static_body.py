from __future__ import annotations

import pygame

from typing import Optional
from pgui.utils.utils_typing import Vec2, Model

class StaticBody:
    def __init__(self):
         # Transform
        self.pos: Vec2 = (0, 0)
        self.size: Vec2 = (32, 32)
        self.rotation: float = 0.0

        # Collision
        self.rect: pygame.Rect = pygame.Rect(self.pos, self.size)
        self.collision_layer: int = 0
        self.collision_mask: list[int] = 0

        # State
        self.visible: bool = True
        self.active: bool = True

        # Render
        self.image: Optional[pygame.Surface] = None
        self.color: Optional[str] = None

    #  Override these in subclasses                                      

    def on_ready(self):
        """Called once when the object is first added to the scene."""
        pass

    def on_collision(self, others: list[Model]):
        """Called when a character collides with this object. Override to handle."""
        pass

    #  Internal update                                                   

    def update(self, surface: pygame.Surface):
        if not self.active: return

        self.rect = pygame.Rect(self.pos, self.size)

        if not self.visible: return

        if self.image:
            self.image = pygame.transform.scale(self.image, self.size)
            image = pygame.transform.rotate(self.image, self.rotation)
            surface.blit(image, self.pos)
        elif self.color:
            pygame.draw.rect(surface, self.color, self.rect)