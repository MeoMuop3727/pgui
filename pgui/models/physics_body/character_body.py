from __future__ import annotations

import pygame
import numpy as np

from typing import Optional
from pgui.utils.utils_typing import Vec2, Model
from pgui.models.animation.animation import Animation

class CharacterBody:  
    def __init__(self):
        # Transform
        self.pos: np.ndarray = np.array([0.0, 0.0])
        self.size: Vec2 = (32, 32)
        self.rotation: float = 0.0

        # Physics
        self.velocity: np.ndarray = np.array([0.0, 0.0])
        self.acceleration: np.ndarray = np.array([0.0, 0.0])
        self.gravity: float = 9.8
        self.mass: float = 1.0
        self.friction: float = 0.8
        self.max_speed: np.ndarray = np.array([300.0, 600.0])

        # Collision
        self.rect: pygame.Rect = pygame.Rect(self.pos, self.size)
        self.collision_layer: int = 0
        self.collision_mask: list[int] = 0

        # State
        self.visible: bool = True
        self.active: bool = True
        self.direction: int = 1              
        self.on_ground: bool = False

        # Animation
        self.animation: Optional[Animation] = None
        self.current_state: str = ""

    #  Override these in subclasses                                      

    def on_ready(self):
        """Called once when the character is first added to the scene."""
        pass

    def on_update(self, dt: float):
        """Game logic — override in subclass (input, AI, state machine...)."""
        pass

    def on_collision(self, others: list[Model]):
        """Called when this character collides with another. Override to handle."""
        pass

    #  Physics helpers                                                   

    def apply_force(self, force: np.ndarray):
        """Adds a force vector to acceleration (F = ma → a += F / m)."""
        self.acceleration += force / self.mass

    def move_x(self, direction: np.ndarray):
        """
        Applies a normalized direction x vector to velocity.
        Call this inside on_update() for movement input.
        """
        self.velocity[0] = direction[0] * self.acceleration[0]

    def move_y(self, direction: np.ndarray):
        """
        Applies a normalized direction y vector to velocity.
        Call this inside on_update() for movement input.
        """
        self.velocity[1] = direction[1] * self.acceleration[1]

    #  Internal update — called by the scene each frame                  

    def update(self, dt: float):
        if not self.active: return

        # User logic first
        self.on_update(dt)

        # Apply gravity
        if not self.on_ground:
            self.velocity[1] += self.gravity * self.mass * dt

        # Apply friction on x when on ground
        if self.on_ground:
            self.velocity[0] *= self.friction

        # Clamp velocity to max_speed
        self.velocity = np.clip(self.velocity, -self.max_speed, self.max_speed)

        # Move
        self.pos += self.velocity * dt

        # Sync rect
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))

        # Reset acceleration each frame
        self.acceleration = np.array([0.0, 0.0])

        # Update animation
        if self.animation and self.visible:
            self.animation.pos = (int(self.pos[0]), int(self.pos[1]))
            self.animation.current_animation = self.current_state
            self.animation.update(dt)