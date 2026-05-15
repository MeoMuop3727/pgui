"""
Panel Module
============
This module provides a container panel UI component built on top of pygame.
The panel renders a styled rectangular frame and provides a subsurface
that child components can draw onto, enabling relative positioning within the panel.

It includes:
- `StylePanel` : Dataclass holding all style/configuration options for a panel.
- `Panel`      : Renders a styled container and delegates rendering to registered child objects.

Typical usage:
>>> def render_content(surface: pygame.Surface):
        pygame.draw.circle(surface, (255, 0, 0), (50, 50), 20)

>>> style = StylePanel(
        pos=(100, 100),
        size=(400, 300),
        bg_color="#ffffff",
        border=2,
        border_color="#aaaaaa"
    )
    panel = Panel(surface, style)
    panel.objects.append(render_content)
    # Inside game loop
    panel.update()
"""

import pygame

from utils.utils_typing import Vec2, ColorType
from utils.utils_transform import hex_to_rbg, to_array

from dataclasses import dataclass

@dataclass
class StylePanel:

    """
    Dataclass containing all visual and layout configuration for a Panel.

    Attributes
    ----------
    pos : Vec2
        Position (x, y) of the panel on the surface. Defaults to (0, 0).
    size : Vec2
        Size (width, height) of the panel frame. Defaults to (500, 500).
    bg_color : ColorType
        Background color of the panel. Defaults to #f0f0f0.
    border_color : ColorType
        Color of the border. Defaults to #000000.
    border_radius : int
        Corner radius for rounded borders. Defaults to 0.
    border : int
        Border thickness in pixels. 0 means no border.
    padding : int
        Reserved for future use — inner spacing between panel edge and content.
    visible : bool
        Whether the panel is rendered. Defaults to True.
    """

    pos: Vec2 = (0, 0)
    size: Vec2 = (500, 500)

    bg_color: ColorType = "#f0f0f0"

    border_color: ColorType = "#000000"
    border_radius: int = 0
    border: int = 0

    padding: int = 0

    visible: bool = True

class Panel:

    """
    A container component that renders a styled rectangular frame and
    provides a subsurface for child components to draw onto.

    Child render functions are stored in ``objects`` and called each frame
    with the panel's subsurface as their argument. This allows child components
    to use coordinates relative to the panel's top-left corner rather than
    the main surface.

    Rendering order (back to front)
    --------------------------------
    1. Border    (slightly larger rect behind the panel)
    2. Background (the main panel rect)
    3. Objects   (each callable in ``objects`` is called with the subsurface)

    Attributes
    ----------
>>> surface : pygame.Surface
    
        The main surface on which the panel frame is drawn.
>>> style : StylePanel
    
        The style/configuration object for this panel.
>>> objects : list[Callable[[pygame.Surface], None]]
    
        List of render functions to call each frame.
        Each function receives the panel's subsurface as its argument.
        Add child render functions here to draw inside the panel.

    Methods
    -------
>>> update() -> None
    
        Draws the border, background, and all registered child objects each frame.
        Does nothing if ``StylePanel.visible`` is False.

>>> get_subsurface(self) -> pygame.Surface

        Return the surface which will be used to draw the objects

    Example
    -------
>>> def draw_hud(surface: pygame.Surface):
            pygame.draw.rect(surface, (255, 0, 0), (10, 10, 50, 20))

>>> style = StylePanel(pos=(50, 50), size=(300, 200), bg_color="#1a1a1a")
        panel = Panel(screen, style)
        panel.objects.append(draw_hud)
        # Inside game loop
        panel.update() # draw_hud will claim the subsurface of panel
    """
    
    def __init__(self,
                 surface: pygame.Surface,
                 style: StylePanel,
                 objects: list = []):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible

        self.__rect = pygame.Rect(self.__style.pos, self.__style.size)

        self.__subrect = self.__surface.subsurface(self.__rect)

        self.objects: list = objects
    
    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value
    
    def update(self) -> None:
        if self.__visible:
            self.__draw_border()
            self.__draw_bg()
            self.__draw_objects()
    
    def get_subsurface(self) -> pygame.Surface:
        return self.__subrect

    def __draw_bg(self) -> None:
        bg = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), bg, border_radius=self.__style.border_radius)

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2
        pos_border = to_array(self.__style.pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)
    
    def __draw_objects(self) -> None:
        if self.objects:
            for object in self.objects: object(self.__subrect)
