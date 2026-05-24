from __future__ import annotations

import pygame
import numpy as np

from typing import Optional
from utils.utils_typing import Vec2, Model
from models.animation import Animation

class RigidBody:
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
        self.restitution: float = 0.3
        self.max_speed: np.ndarray = np.array([600.0, 1200.0])
 
        # Collision
        self.rect: pygame.Rect = pygame.Rect(self.pos, self.size)
        self.collision_layer: int = 0
        self.collision_mask: int = 0
 
        # State
        self.visible: bool = True
        self.active: bool = True
        self.on_ground: bool = False
 
        # Render
        self.animation: Optional[Animation] = None
        self.current_state: str = ""
    
    # ------------------------------------------------------------------ #
    #  Override these in subclasses                                      #
    # ------------------------------------------------------------------ #
 
    def on_ready(self):
        """Called once when the body is first added to the scene."""
        pass
 
    def on_update(self, dt: float):
        """Called every frame before physics. Override to extend behavior."""
        pass
 
    def on_collision(self, others: list[Model]):
        """Called when this body collides with another. Override to handle."""
        pass

    # ------------------------------------------------------------------ #
    #  Physics helpers                                                   #
    # ------------------------------------------------------------------ #
 
    def apply_force(self, force: np.ndarray):
        """Adds a force vector to acceleration (F = ma → a += F / m)."""
        self.acceleration += force / self.mass
 
    def apply_impulse(self, impulse: np.ndarray):
        """Adds a direct velocity change, bypassing mass (for knockback, jumps, etc.)."""
        self.velocity += impulse
    
    # ------------------------------------------------------------------ #
    #  Internal update — called by the scene each frame                  #
    # ------------------------------------------------------------------ #
 
    def update(self, dt: float):
        if not self.active: return
 
        self.on_update(dt)
 
        # Apply gravity
        if not self.on_ground:
            self.velocity[1] += self.gravity * self.mass * dt
 
        # Apply friction when grounded
        if self.on_ground:
            self.velocity[0] *= self.friction
 
        # Integrate acceleration into velocity
        self.velocity += self.acceleration * dt
 
        # Clamp velocity
        self.velocity = np.clip(self.velocity, -self.max_speed, self.max_speed)
 
        # Move
        self.pos += self.velocity * dt
 
        # Sync rect
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))
 
        # Reset acceleration
        self.acceleration = np.array([0.0, 0.0])
 
        # Render
        if self.animation and self.visible:
            self.animation.pos = (int(self.pos[0]), int(self.pos[1]))
            self.animation.current_animation = self.current_state
            self.animation.update(dt)