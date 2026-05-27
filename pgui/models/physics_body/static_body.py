from __future__ import annotations

import pygame

from typing import Optional
from pgui.utils.utils_typing import Vec2, Model

class StaticBody:
    
    """
    A base class for stationary objects in a pygame game.

    Does not simulate physics — position never changes after placement.
    Participates in collision detection via ``rect``, ``collision_layer``,
    and ``collision_mask``. Subclass this for walls, platforms, obstacles,
    and props.

    Rendering supports either an image surface or a solid color rect.
    If both are set, ``image`` takes priority.

    Attributes
    ----------
        >>> pos : Vec2

                Position of the object as (x, y). Defaults to (0, 0).

        >>> size : Vec2

                Width and height of the object. Defaults to (32, 32).

        >>> rotation : float

                Rotation angle in degrees applied to the image on render.
                Defaults to 0.0.

        >>> rect : pygame.Rect

                Bounding rect used for collision detection, synced to ``pos``
                and ``size`` each frame.

        >>> collision_layer : int

                Bitmask defining which layer this object belongs to.

        >>> collision_mask : int

                Bitmask defining which layers this object collides with.

        >>> visible : bool

                Whether the object is rendered. Defaults to True.

        >>> active : bool

                Whether the object is updated and participates in collision.
                Defaults to True.

        >>> image : pygame.Surface, optional

                Static surface to render. Scaled to ``size`` each frame.
                Defaults to None.

        >>> color : str, optional

                Fallback color used to render a solid rect if ``image`` is None.
                Defaults to None.

        Methods
        -------
        >>> on_ready() -> None

                Hook called once when the object is first added to the scene.
                Override to run initialization logic.

        >>> on_collision(other: list[CharacterBody]) -> None

                Hook called when characters collide with this object.
                Override to implement collision response logic.

        >>> update(surface: pygame.Surface) -> None

                Syncs rect, then renders the image or color rect onto the surface.
                Called automatically by the scene each frame.

        Example
        -------
        >>> class Platform(StaticBody):
                def __init__(self):
                super().__init__()
                self.pos = (0, 500)
                self.size = (800, 32)
                self.color = "#555555"
                def on_collision(self, others):
                for other in others:
                        other.on_ground = True
    """

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

    # ------------------------------------------------------------------ #
    #  Override these in subclasses                                      #
    # ------------------------------------------------------------------ #

    def on_ready(self):
        """Called once when the object is first added to the scene."""
        pass

    def on_collision(self, others: list[Model]):
        """Called when a character collides with this object. Override to handle."""
        pass

    # ------------------------------------------------------------------ #
    #  Internal update                                                   #
    # ------------------------------------------------------------------ #

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