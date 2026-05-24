from __future__ import annotations

import pygame
import numpy as np

from typing import Optional
from utils.utils_typing import Vec2, Model
from models.animation.animation import Animation

class CharacterBody:  
    
    """
    A base class for physics-driven characters in a pygame game.

    Provides built-in gravity, friction, velocity, and acceleration simulation,
    as well as rect syncing and animation state management. Subclass this to
    create players, enemies, NPCs, or any moving entity.

    Subclasses should override the hook methods (``on_ready``, ``on_update``,
    ``on_collision``) to implement custom behavior. The core ``update()`` method
    handles the physics pipeline automatically each frame.

    Attributes
    ----------
>>> pos : np.ndarray

        Position of the character as [x, y]. Defaults to [0.0, 0.0].

>>> size : Vec2

        Width and height of the character. Defaults to (32, 32).

>>> rotation : float

        Rotation angle in degrees. Defaults to 0.0.

>>> velocity : np.ndarray

        Current velocity as [vx, vy]. Defaults to [0.0, 0.0].

>>> acceleration : np.ndarray

        Current acceleration as [ax, ay]. Reset to zero each frame.

>>> gravity : float

        Gravitational pull applied to velocity[1] each frame when not on ground.
        Defaults to 9.8.

>>> mass : float

        Mass of the character, affects force application and gravity.
        Defaults to 1.0.

>>> friction : float

        Horizontal velocity multiplier applied when on ground. Defaults to 0.8.

>>> max_speed : np.ndarray

        Maximum speed clamped on each axis as [max_vx, max_vy].
        Defaults to [300.0, 600.0].

>>> rect : pygame.Rect

        Bounding rect synced to ``pos`` and ``size`` each frame.

>>> collision_layer : int

        Bitmask defining which layer this character belongs to.

>>> collision_mask : int

        Bitmask defining which layers this character collides with.

>>> visible : bool

        Whether the animation is rendered. Defaults to True.

>>> active : bool

        Whether the character is updated each frame. Defaults to True.

>>> direction : int

        Facing direction. 1 = right, -1 = left.

>>> on_ground : bool

        Whether the character is currently standing on the ground.

>>> animation : Animation, optional

        Animation component to render. Defaults to None.

>>> current_state : str

        Current animation state key (e.g. ``"idle"``, ``"run"``).

    Methods
    -------
>>> on_ready() -> None

        Hook called once when the character is first added to the scene.
        Override to run initialization logic.

>>> on_update(dt: float) -> None

        Hook called every frame before physics are applied.
        Override to implement input handling, AI, or state machines.

>>> on_collision(other: CharacterBody) -> None

        Hook called when this character collides with another.
        Override to implement collision response logic.

>>> apply_force(force: np.ndarray) -> None

        Adds a force vector to acceleration using F = ma.

>>> move(direction: np.ndarray) -> None

        Applies a direction vector to velocity scaled by acceleration.

>>> update(dt: float) -> None

        Main update loop. Runs physics, syncs rect, and updates animation.
        Called automatically by the scene each frame.

    Example
    -------
>>> class Player(CharacterBody):
        def __init__(self, surface: pygame.Surface):
            super().__init__()
        def on_update(self, dt):
            keys = pygame.key.get_pressed()
            direction = np.array([0.0, 0.0])
            if keys[pygame.K_LEFT]: direction[0] = -1
            if keys[pygame.K_RIGHT]: direction[0] = 1
            if keys[pygame.K_SPACE] and self.on_ground:
                self.velocity[1] = -500.0
                self.on_ground = False         
            if self.pos[1] <= 10:
                self.pos[1] = 10
                self.velocity[1] = 500
            if self.pos[1] >= 300:
                self.pos[1] = 300
                self.on_ground = True
            self.acceleration = np.array([500.0, 0.0])
            self.move_x(direction)
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

    # ------------------------------------------------------------------ #
    #  Override these in subclasses                                      #
    # ------------------------------------------------------------------ #

    # ------------------------------------------------------------------ #
    #  Override these in subclasses                                      #
    # ------------------------------------------------------------------ #

    def on_ready(self):
        """Called once when the character is first added to the scene."""
        pass

    def on_update(self, dt: float):
        """Game logic — override in subclass (input, AI, state machine...)."""
        pass

    def on_collision(self, others: list[Model]):
        """Called when this character collides with another. Override to handle."""
        pass

    # ------------------------------------------------------------------ #
    #  Physics helpers                                                   #
    # ------------------------------------------------------------------ #

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

    # ------------------------------------------------------------------ #
    #  Internal update — called by the scene each frame                  #
    # ------------------------------------------------------------------ #

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