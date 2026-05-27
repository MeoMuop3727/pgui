"""
Scene Module
============
This module provides the base class for all game scenes in a pygame application.

A scene represents a distinct game state — such as a main menu, gameplay screen,
pause screen, or cutscene. Each scene is self-contained, managing its own
event handling, logic updates, and rendering.

Scenes are designed to be used alongside `ManageScene`, which drives the
main game loop and manages scene transitions via a stack.

It includes:
- `Scene` : Base class defining the interface for all game scenes.

Typical usage:
>>> class GameScene(Scene):
        def on_enter(self):
            self.player = Player()
        def handle_event(self, events):
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.manager.pop_scene()
        def update(self, delta):
            self.player.update(delta)
        def render(self, screen):
            screen.fill((0, 0, 0))
            self.player.render(screen)
"""

import pygame
class Scence:

    """
    Abstract base class representing a single game scene.

    A scene encapsulates a distinct game state — such as a main menu,
    gameplay screen, or pause screen. Scenes are managed by `ManageScene`
    via a stack, with only the top scene being active at any given time.

    Subclass this and override the relevant methods to implement
    custom behavior for each scene.

    Attributes
    ----------
>>> manager : ManageScene or None

        Reference to the scene manager. Assigned automatically
        when the scene is pushed onto the stack.

    Methods
    -------
>>> on_enter() -> None

        Called once when the scene is pushed onto the stack.
        Use for initialization or reset logic.

>>> on_exit() -> None
    
        Called once when the scene is popped off the stack.
        Use for cleanup logic.
    
>>> handle_event(events) -> None
    
        Called each frame with the list of pygame events.
        Use to handle input and user interactions.
    
>>> update(delta) -> None
    
        Called each frame with the delta time in seconds.
        Use to update game logic and state.
    
>>> render(screen) -> None
    
        Called each frame with the main display surface.
        Use to draw the scene content.

    Example
    -------
>>> class MainMenuScene(Scene):
            def on_enter(self):
                print("Entering main menu")
            def handle_event(self, events):
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        self.manager.push_scene(GameScene())
            def render(self, screen):
                screen.fill((0, 0, 0))
    """

    def __init__(self) -> None:
        from pgui.components.scenes.manager_scene import ManageScence
        
        """
        Initialize the scene with no manager assigned.
        """

        self.manager: ManageScence = None
    
    def on_enter(self) -> None:
        """
        Called once when this scene is pushed onto the scene stack.

        Override to perform setup, load assets, or reset state.
        """
         
        pass

    def on_exit(self) -> None:
        """
        Called once when this scene is popped off the scene stack.

        Override to perform cleanup, save state, or release resources.
        """

        pass

    def handle_event(self, events: list[pygame.event.Event]) -> None:
        """
        Called each frame to process pygame events.

        Parameters
        ----------
        events : list[pygame.event.Event]
            The list of events returned by `pygame.event.get()`.
        """

        pass
    
    def update(self, dental: float) -> None:
        """
        Called each frame to update scene logic.

        Parameters
        ----------
        delta : float
            Time elapsed since the last frame, in seconds.
            Use for frame-rate independent movement and animations.
        """

        pass
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Called each frame to draw the scene onto the screen.

        Parameters
        ----------
        screen : pygame.Surface
            The main display surface to render onto.
        """

        pass

