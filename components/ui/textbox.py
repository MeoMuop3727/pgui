"""
TextBox Module
==============
This module provides a static text display component built on top of pygame.
Text is automatically word-wrapped to fit within the box's width,
with support for padding, border, and background styling.

It includes:
- `StyleTextBox` : Dataclass holding all style/configuration options for a text box.
- `TextBox`      : Renders wrapped text inside a styled rectangular frame.

Typical usage:
>>> style = StyleTextBox(
        content="Hello, this is a text box.",
        size=(500, 400),
        padding=10,
        bg_color="#f0f0f0"
    )
    textbox = TextBox(surface, style)
    # Inside game loop
    textbox.update()
"""

import pygame

from dataclasses import dataclass
from typing import List
from utils.utils_typing import Vec2, ColorType

from utils.utils_transform import to_array, hex_to_rbg

@dataclass(slots=True)
class StyleTextBox:

    """
    Dataclass containing all visual and layout configuration for a TextBox.

    Attributes
    ----------
    content : str
        The text content to display. Words are automatically wrapped
        to fit within the box width minus padding.
    font : pygame.font.Font
        Font used to render the text.
    color : ColorType
        Text color.
    bg_color : ColorType
        Background color of the text box frame.
    antialias : bool
        Whether to apply antialiasing to rendered text. Defaults to True.
    pos : Vec2
        Position (x, y) of the text box on the surface.
    size : Vec2
        Size (width, height) of the text box.
    border : int
        Border thickness in pixels. 0 means no border.
    border_radius : int
        Corner radius for rounded borders.
    border_color : ColorType
        Color of the border.
    padding : int
        Inner spacing in pixels between the box edge and the text.
    line_height : int
        Reserved for future use — additional spacing between lines.
    visible : bool
        Whether the text box is rendered. Defaults to True.
    """

    content: str = ""
    font: pygame.font.Font = pygame.font.Font(None, 25)
    color: ColorType = "#333333"
    bg_color: ColorType = "#cccccc"
    antialias: bool = True
    pos: Vec2 = (0, 0)
    size: Vec2 = (500, 400)
    border: int = 0
    border_radius: int = 0
    border_color: ColorType = "#000000"
    padding: int = 0
    line_height: int = 0
    visible: bool = True

class TextBox: 

    """
    A static text display component that renders word-wrapped text
    inside a styled rectangular frame.

    Text is wrapped automatically based on the box width and padding.
    Each line is rendered top-to-bottom with spacing derived from
    the font's line height.

    Rendering order (back to front)
    --------------------------------
    1. Border      (slightly larger rect behind the frame)
    2. Background  (the main frame rect)
    3. Text        (word-wrapped lines, offset by padding)

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which the text box is drawn.

>>> style : StyleTextBox

        The style/configuration object for this text box.

    Methods
    -------
>>> update() -> None

        Draws the border, background, and wrapped text each frame.
        Does nothing if `StyleTextBox.visible` is False.

    Example
    -------
>>> style = StyleTextBox(
            content="This is a long text that will be wrapped automatically.",
            size=(400, 300),
            padding=12,
            bg_color="#ffffff",
            border=2,
            border_color="#aaaaaa"
        )
        textbox = TextBox(surface, style)
        # Inside game loop
        textbox.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleTextBox):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos

        self.__rect = pygame.Rect(self.__pos, self.__style.size)

        self.__list_text = self.__wrap_text()
    
    @property
    def pos(self) -> Vec2:
        return self.__pos

    @pos.setter
    def pos(self, new_pos: Vec2):
        self.__pos = new_pos
    
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

    def __draw_frame(self) -> None:
        frame = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), frame, border_radius=self.__style.border_radius)

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        pos_border = to_array(self.__pos) - to_array(border_width)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)
    
    def __wrap_text(self) -> List[str]:
        list_text: List[str] = []

        current_line = ""
        max_width = self.__style.size[0] - 2 * self.__style.padding

        for text in self.__style.content.split(" "):
            text_line = text if current_line == "" else current_line + " " + text

            text_width = self.__style.font.size(text_line)[0]

            if text_width <= max_width:
                current_line = text_line
            else:
                if current_line:
                    list_text.append(current_line)
                current_line = text

        if current_line:
            list_text.append(current_line)

        return list_text

    def __draw_content(self) -> None:
        for line, text_line in enumerate(self.__list_text):
            text_surface = self.__style.font.render(text_line, self.__style.antialias, hex_to_rbg(self.__style.color))
            text_rect = to_array(self.__pos) + to_array((0, text_surface.get_height() * line)) + to_array((self.__style.padding, self.__style.padding))

            self.__surface.blit(text_surface, (int(text_rect[0]), int(text_rect[1])))

