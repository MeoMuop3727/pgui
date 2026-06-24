"""
PGUI scene system provides the foundational building blocks for organizing and managing
game states. It offers a Scene base class for defining individual game screens or states,
and a ManageScene controller for handling transitions and the active scene lifecycle
within a pygame application.
"""

from pgui.components.scenes.manager_scene import ManageScene
from pgui.components.scenes.scene import Scene

__all__ = ["ManageScene", "Scene"]