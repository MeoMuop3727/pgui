"""A collection of physics body types used in pgui."""

from models.physics_body.character_body import CharacterBody
from models.physics_body.static_body import StaticBody
from models.physics_body.rigid_body import RigidBody

__all__ = [
    "CharacterBody",
    "StaticBody",
    "RigidBody"
]