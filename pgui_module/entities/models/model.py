import pygame
from typing import Optional
from .animation import Animation

class Model:
    """
    Base class for all entities in game (NPC, Player, Enemy,...).
    Inherit this class to build particular entities.
    """

    def __init__(self,
                 position: pygame.Vector2 = None,
                 tag: str = "entity",
                 sprite: pygame.Surface = None):
        # --- Transform ---
        self.position = position or pygame.Vector2(0, 0)                # x, y
        self.rotation: float = 0.0                                      # degree and clockwise
        self.scale: pygame.Vector2 = pygame.Vector2(1, 1)               # width, height

        # --- Physics ---
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)            # current speed (pixel/s), add to position each frame
        self.acceleration: pygame.Vector2 = pygame.Vector2(0, 0)        # add to velocity each frame and reset to 0
        self.mass: float = 1.0                                          # volume of the entity, entity is heavier will have smaller acceleration
        self.friction: float = 0.85                                     # 0.0 = no friction, 1.0 = always has friction
        self.gravity: float = 0.0                                       # pixel/s², 0 = no gravity
        self.is_grounded: bool = False                                  # on the ground

        # --- Collision ---
        self._collider_offset: pygame.Vector2 = pygame.Vector2(0, 0)    # move collider of the entity
        self._collider_size: pygame.Vector2 = None                      # size of collider, None = use the size of the sprite

        # --- Sprite ---
        self.sprite: Optional[pygame.Surface] = sprite                  # current surface is being drawn
        self._original_sprite: Optional[pygame.Surface] = sprite        # save the original frame after scale/rotate

        # --- Animation ---
        self._animations: dict[str, Animation] = {}                     # store all ordered animation
        self._current_anim: Optional[str] = None                        # name of animation being run

        # --- Entity info ---
        self.tag: str = tag                                             # To classify entities
        self.is_active: bool = True                                     # False, pass the entity without delete it
        self.is_visible: bool = True                                    # False, no render
        self.layer: int = 0                                             # z-order, the layer to draw

    # =========================================================
    # Transform
    # =========================================================

    def move(self, dx: float, dy: float):
        self.position.x += dx
        self.position.y += dy

    def set_position(self, x: float, y: float):
        self.position = pygame.Vector2(x, y)

    def set_rotation(self, angle: float):
        self.rotation = angle % 360
        self._apply_transform()

    def set_scale(self, sx: float, sy: float = None):
        self.scale = pygame.Vector2(sx, sy if sy is not None else sx)
        self._apply_transform()

    def _apply_transform(self):
        if self._original_sprite is None: return

        w = int(self._original_sprite.get_width() * self.scale.x)
        h = int(self._original_sprite.get_height() * self.scale.y)
        scaled = pygame.transform.scale(self._original_sprite, (w, h))
        self.sprite = pygame.transform.rotate(scaled, -self.rotation)

    # =========================================================
    # Physics
    # =========================================================

    def apply_force(self, fx: float, fy: float):
        """F = ma → a = F/m"""
        self.acceleration.x += fx / self.mass
        self.acceleration.y += fy / self.mass

    def _update_physics(self, dt: float):
        # Gravity
        if not self.is_grounded:
            self.velocity.y += self.gravity * dt

        # Acceleration → Velocity
        self.velocity += self.acceleration * dt
        self.acceleration = pygame.Vector2(0, 0)

        # Friction 
        if self.is_grounded:
            self.velocity.x *= self.friction

        # Velocity → Position
        self.position += self.velocity * dt

    # =========================================================
    # Collision
    # =========================================================

    def set_collider(self, width: float, height: float, offset_x: float = 0, offset_y: float = 0):
        """Adjust collider, defaut = size of sprite"""
        self._collider_size = pygame.Vector2(width, height)
        self._collider_offset = pygame.Vector2(offset_x, offset_y)

    def get_rect(self) -> pygame.Rect:
        """Get collision rect in the world position"""
        if self._collider_size:
            w, h = int(self._collider_size.x), int(self._collider_size.y)
        elif self.sprite:
            w, h = self.sprite.get_size()
        else:
            w, h = 16, 16  # fallback

        x = int(self.position.x + self._collider_offset.x - w / 2)
        y = int(self.position.y + self._collider_offset.y - h / 2)
        return pygame.Rect(x, y, w, h)

    def collides_with(self, other: "Model") -> bool:
        return self.get_rect().colliderect(other.get_rect())

    # =========================================================
    # Animation
    # =========================================================

    def add_animation(self, name: str, animation: Animation):
        self._animations[name] = animation

    def play_animation(self, name: str, force_restart: bool = False):
        if name not in self._animations: return
        if self._current_anim == name and not force_restart: return

        self._current_anim = name
        self._animations[name].reset()

    def _update_animation(self, dt: float):
        if self._current_anim is None: return

        anim = self._animations[self._current_anim]
        anim.update(dt)
        self.sprite = anim.get_frame()
        self._original_sprite = self.sprite

    # =========================================================
    # Update / Draw
    # =========================================================

    def update(self, dt: float):
        """Call each frame. Override in the subclass to add logic."""
        if not self.is_active: return

        self._update_physics(dt)
        self._update_animation(dt)

    def draw(self, surface: pygame.Surface, camera_offset: pygame.Vector2 = None):
        """Draw the sprite on surface. camera_offset will support the camera."""
        if not self.is_visible or self.sprite is None: return

        offset = camera_offset or pygame.Vector2(0, 0)
        draw_x = self.position.x - self.sprite.get_width() / 2 - offset.x
        draw_y = self.position.y - self.sprite.get_height() / 2 - offset.y
        surface.blit(self.sprite, (int(draw_x), int(draw_y)))

    def draw_debug(self, surface: pygame.Surface, camera_offset: pygame.Vector2 = None):
        """Draw collider rect to debug"""
        offset = camera_offset or pygame.Vector2(0, 0)
        rect = self.get_rect()
        rect.x -= int(offset.x)
        rect.y -= int(offset.y)
        pygame.draw.rect(surface, (255, 0, 0), rect, 1)

    # =========================================================
    # Helpers
    # =========================================================

    def distance_to(self, other: "Model") -> float:
        return self.position.distance_to(other.position)

    def direction_to(self, other: "Model") -> pygame.Vector2:
        delta = other.position - self.position
        if delta.length() == 0: return pygame.Vector2(0, 0)
        return delta.normalize()

    def __repr__(self):
        return f"<Model tag='{self.tag}' pos={self.position} active={self.is_active}>"