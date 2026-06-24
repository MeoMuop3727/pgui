import pygame
class Scene:

    """
    Abstract base class representing a single game scene.

    A scene encapsulates a distinct game state — such as a main menu,
    gameplay screen, or pause screen. Scenes are managed by `ManageScene`
    via a stack, with only the top scene being active at any given time.

    Subclass this and override the relevant methods to implement
    custom behavior for each scene.
    """

    def __init__(self) -> None:
        from pgui.components.scenes.manager_scene import ManageScene
        
        """
        Initialize the scene with no manager assigned.
        """

        self.manager: ManageScene = None
    
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
    
    def update(self, dt: float) -> None:
        """
        Called each frame to update scene logic.

        Parameters
        ----------
        dt : float
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

