import pygame, sys
from pgui.components.scenes.scene import Scene
from pgui.utils.utils_typing import Number

class ManageScene:

    """
    Stack-based scene manager that drives the main pygame game loop.

    Maintains an ordered stack of `Scene` objects. Only the top scene
    is active — receiving events, updates, and render calls each frame.
    Scenes can be pushed, popped, or replaced to handle transitions
    between game states.
    """

    def __init__(self, screen: pygame.Surface):
        self.__screen = screen

        self.__scenes: list[Scene] = []
        self.__running = True
        self.__clock = pygame.time.Clock()
        
    def get_scenes(self) -> list[Scene]:
        """Return stack scenes @scene"""
        return self.__scenes

    def push_scene(self, scene: Scene) -> None:
        """
        Push a new scene onto the top of the stack and activate it.

        Assigns this manager to the scene, appends it to the stack,
        and calls `scene.on_enter()`.

        Parameters
        ----------
        scene : Scene
            The scene to push onto the stack.
        """

        scene.manager = self
        self.__scenes.append(scene)
        scene.on_enter()

    def pop_scene(self) -> None:
        """
        Pop the top scene off the stack and deactivate it.

        Calls `scene.on_exit()` on the removed scene.
        Does nothing if the stack is empty.
        """
        
        if self.__scenes:
            scene = self.__scenes.pop()
            scene.on_exit()
    
    def replace_scene(self, scene: Scene) -> None:
        """
        Replace the current top scene with a new one.

        Equivalent to calling `pop_scene()` followed by `push_scene()`.

        Parameters
        ----------
        scene : Scene
            The scene to replace the current top scene with.
        """

        self.pop_scene()
        self.push_scene(scene)
    
    def get_current_scene(self) -> Scene:
        """
        Return the scene currently at the top of the stack.

        Returns
        -------
        Scene or None
            The active scene, or None if the stack is empty.
        """

        return self.__scenes[-1] if self.__scenes else None
    
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

            current_scene = self.get_current_scene()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if not current_scene: continue

            current_scene.handle_event(events)
            current_scene.render(self.__screen)
            current_scene.update(dt)

            pygame.display.flip()
            