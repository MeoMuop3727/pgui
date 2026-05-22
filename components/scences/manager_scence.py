"""
ManageScene Module
==================
This module provides a stack-based scene management system for pygame applications.

Scenes are pushed onto and popped off a stack, with only the top scene
being active at any given time. This allows for clean transitions between
game states such as menus, gameplay, and pause screens.

It includes:
- `ManageScene` : Manages the scene stack and drives the main game loop.

Typical usage:
>>> screen = pygame.display.set_mode((800, 600))

>>> manager = ManageScene(screen)
>>> manager.push_scene(MainMenuScene())

>>> manager.run(fps=60)
"""

import pygame, sys
from components.scences.scence import Scence
from utils.utils_typing import Number

class ManageScence:

    """
    Stack-based scene manager that drives the main pygame game loop.

    Maintains an ordered stack of `Scene` objects. Only the top scene
    is active — receiving events, updates, and render calls each frame.
    Scenes can be pushed, popped, or replaced to handle transitions
    between game states.

    Attributes
    ----------
>>> screen : pygame.Surface

        The main display surface passed to the active scene each frame.

    Example
    -------
>>> manager = ManageScene(screen)
        manager.push_scene(MainMenuScene())
        manager.run(fps=60)
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the scene manager.

        Parameters
        ----------
        screen : pygame.Surface
            The main display surface used for rendering.
        """

        self.__screen = screen

        self.__scences: list[Scence] = []
        self.__running = True
        self.__clock = pygame.time.Clock()
        
    def get_scences(self) -> list[Scence]:
        """Return stack scences @Scence"""
        return self.__scences

    def push_scence(self, scence: Scence) -> None:
        """
        Push a new scene onto the top of the stack and activate it.

        Assigns this manager to the scene, appends it to the stack,
        and calls `scene.on_enter()`.

        Parameters
        ----------
        scene : Scene
            The scene to push onto the stack.
        """

        scence.manager = self
        self.__scences.append(scence)
        scence.on_enter()

    def pop_scence(self) -> None:
        """
        Pop the top scene off the stack and deactivate it.

        Calls `scene.on_exit()` on the removed scene.
        Does nothing if the stack is empty.
        """
        
        if self.__scences:
            scence = self.__scences.pop()
            scence.on_exit()
    
    def replace_scence(self, scence: Scence) -> None:
        """
        Replace the current top scene with a new one.

        Equivalent to calling `pop_scene()` followed by `push_scene()`.

        Parameters
        ----------
        scene : Scene
            The scene to replace the current top scene with.
        """

        self.pop_scence()
        self.push_scence(scence)
    
    def get_current_scence(self) -> Scence:
        """
        Return the scene currently at the top of the stack.

        Returns
        -------
        Scene or None
            The active scene, or None if the stack is empty.
        """

        return self.__scences[-1] if self.__scences else None
    
    def run(self, fps: Number = 60) -> None:
        """
        Start the main game loop.

        Each frame, the loop:
        1. Ticks the clock and computes delta time (in seconds).
        2. Collects all pygame events.
        3. Quits the application if a QUIT event is received.
        4. Delegates events, update, and render to the active scene.
        5. Flips the display buffer.

        The loop runs until the application is closed.

        Parameters
        ----------
        fps : int or float
            Target frames per second. Defaults to 60.
        """
        
        while self.__running:
            dt = self.__clock.tick(fps) / 1e3

            events = pygame.event.get()

            current_scence = self.get_current_scence()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if not current_scence: continue

            current_scence.handle_event(events)
            current_scence.render(self.__screen)
            current_scence.update(dt)

            pygame.display.flip()
            