from __future__ import annotations

import pygame
import numpy as np

from typing import Optional
from pgui.utils.utils_typing import Vec2, Model
from pgui.models.animation import Animation

class RigidBody:

    """
    A base class for physics-simulated objects in a pygame game.

    Simulates forces, velocity, gravity, and friction automatically
    each frame. Unlike CharacterBody, movement is entirely driven
    by the physics pipeline — not by direct input. Subclass this
    for crates, projectiles, debris, or any object governed by physics.

    Subclasses should override the hook methods (on_ready, on_update,
    on_collision) to implement custom behavior without touching
    the physics pipeline.

    Attributes
    ----------
    pos : np.ndarray

        Position of the body as [x, y]. Defaults to [0.0, 0.0].

    size : Vec2

        Width and height of the body. Defaults to (32, 32).

    rotation : float

        Rotation angle in degrees. Defaults to 0.0.

    velocity : np.ndarray

        Current velocity as [vx, vy]. Defaults to [0.0, 0.0].

    acceleration : np.ndarray

        Accumulated acceleration this frame. Reset to zero after each update.

    gravity : float

        Gravitational pull applied to velocity[1] each frame when not on ground.
        Defaults to 9.8.

    mass : float

        Mass of the body. Affects force application and gravity scaling.
        Defaults to 1.0.

    friction : float

        Horizontal velocity multiplier applied when on ground. Defaults to 0.8.

    restitution : float

        Bounciness factor on collision response (0.0 = no bounce, 1.0 = full bounce).
        Defaults to 0.3.

    max_speed : np.ndarray

        Maximum speed clamped on each axis as [max_vx, max_vy].
        Defaults to [600.0, 1200.0].

    rect : pygame.Rect

        Bounding rect synced to pos and size each frame.

    collision_layer : int

        Bitmask defining which layer this body belongs to.

    collision_mask : int

        Bitmask defining which layers this body collides with.

    visible : bool

        Whether the body is rendered. Defaults to True.

    active : bool

        Whether the body is updated each frame. Defaults to True.

    on_ground : bool

        Whether the body is currently resting on the ground.

    animation : Animation, optional

        Animation component to render. Defaults to None.

    current_state : str

        Current animation state key.

    Methods
    -------
    on_ready() -> None

        Hook called once when the body is first added to the scene.
        Override to run initialization logic.

    on_update(dt: float) -> None

        Hook called every frame before physics are applied.
        Override to extend behavior.

    on_collision(others: list[Model]) -> None

        Hook called when this body collides with another object.
        Override to implement collision response logic.

    apply_force(force: np.ndarray) -> None

        Adds a force vector to acceleration using F = ma.

    apply_impulse(impulse: np.ndarray) -> None

        Adds a one-time velocity change directly, bypassing mass.

    update(dt: float) -> None

        Main update loop. Runs physics, syncs rect, and updates animation.
        Called automatically by the scene each frame.

    Example
    -------
    >>> class Crate(RigidBody):
        def __init__(self):
            super().__init__()
            self.pos = np.array([200.0, 100.0])
            self.mass = 5.0
            self.restitution = 0.1
            self.color = "#8B5E3C"
        def on_collision(self, others):
            for other in others:
                self.on_ground = True
                self.velocity[1] = -abs(self.velocity[1]) * self.restitution
    """

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