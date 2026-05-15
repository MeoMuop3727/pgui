"""
Label Module
============
This module provides a static text label UI component built on top of pygame.
The label renders centered text inside a styled rectangular frame,
with support for border, background color, and dynamic content updates.

It includes:
- `StyleLabel` : Dataclass holding all style/configuration options for a label.
- `Label`      : Renders a styled text label with a background frame and optional border.

Typical usage:
>>> style = StyleLabel(
        content="Hello World",
        color="#ffffff",
        bg_color="#333333",
        size=(200, 50),
        pos=(100, 100)
    )
    label = Label(surface, style)
    # Inside game loop
    label.update()
    # Update text dynamically
    label.content = "New Text"
"""

import pygame

from dataclasses import dataclass
from utils.utils_typing import Vec2, ColorType

from utils.utils_transform import to_array, hex_to_rbg

@dataclass(slots=True)
class StyleLabel:

    """
    Dataclass containing all visual and layout configuration for a Label.

    Attributes
    ----------
    content : str
        The text displayed inside the label. Defaults to empty string.
    font : pygame.font.Font
        Font used to render the label text.
    color : ColorType
        Text color. Defaults to #333333.
    bg_color : ColorType
        Background color of the label frame. Defaults to #cccccc.
    antialias : bool
        Whether to apply antialiasing to rendered text. Defaults to True.
    pos : Vec2
        Position (x, y) of the label on the surface.
    size : Vec2
        Size (width, height) of the label frame.
    border : int
        Border thickness in pixels. 0 means no border.
    border_radius : int
        Corner radius for rounded borders. Defaults to 0.
    border_color : ColorType
        Color of the border. Defaults to #000000.
    visible : bool
        Whether the label is rendered. Defaults to True.
    """

    content: str = ""
    font: pygame.font.Font = pygame.font.Font(None, 25)
    color: ColorType = "#333333"
    bg_color: ColorType = "#cccccc"
    antialias: bool = True
    pos: Vec2 = (0, 0)
    size: Vec2 = (200, 50)
    border: int = 0
    border_radius: int = 0
    border_color: ColorType = "#000000"
    visible: bool = True

class Label: 

    """
    A static text label that renders centered text inside a styled rectangular frame.

    The label text can be updated dynamically at any time via the ``content`` property
    without needing to recreate the component.

    Rendering order (back to front)
    --------------------------------
    1. Border   (slightly larger rect behind the frame)
    2. Frame    (the main background rect)
    3. Text     (centered horizontally and vertically within the frame)

    Attributes
    ----------
>>> surface : pygame.Surface
    
        The surface on which the label is drawn.
    
>>> style : StyleLabel
    
        The style/configuration object for this label.

    Properties
    ----------
>>> content : str
    
        Gets or sets the text displayed inside the label.
        Changes are reflected immediately on the next ``update()`` call.

    Methods
    -------
>>> update() -> None
    
        Draws the border, background frame, and centered text each frame.
        Does nothing if ``StyleLabel.visible`` is False.

    Example
    -------
>>> style = StyleLabel(
            content="Score: 0",
            color="#ffffff",
            bg_color="#222222",
            size=(150, 40),
            pos=(10, 10)
        )
        label = Label(surface, style)
        # Inside game loop
        label.update()
        # Update dynamically
        label.content = f"Score: {score}"
    """
    
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleLabel):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible

        self.__rect = pygame.Rect(self.__style.pos, self.__style.size)

        self.__text = self.__style.content

    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value
        
    def update(self) -> None:
        if self.__visible:
            self.__draw_border()
            self.__draw_frame()
            self.__draw_content()
    
    @property
    def content(self) -> str:
        return self.__text
    
    @content.setter
    def content(self, content: str) -> None:
        self.__text = content

    def __draw_frame(self) -> None:
        frame = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), frame, border_radius=self.__style.border_radius)

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        pos_border = to_array(self.__style.pos) - to_array(border_width)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)

    def __draw_content(self) -> None:
        text_surface = self.__style.font.render(self.__text, self.__style.antialias, hex_to_rbg(self.__style.color))
        text_rect = text_surface.get_rect(center=self.__rect.center)
        self.__surface.blit(text_surface, text_rect)

