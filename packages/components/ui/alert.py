"""
Alert Module
============
This module provides a dismissible alert/notification UI component built on top of pygame.
It combines a styled title bar, a content text box, and a close button into one widget.

Alert types determine the default title bar color when no custom color is provided:
- ``error``   : red    #e74c3c
- ``warning`` : orange #f39c12
- ``success`` : green  #27ae60
- ``info``    : blue   #3498db

It includes:
- `StyleAlert` : Dataclass holding all style/configuration options for an alert.
- `Alert`      : Renders a typed alert box with a title bar, content area, and close button.

Typical usage:
    >>> style = StyleAlert(
         title="Success",
         content="Your file has been saved successfully.",
         type="success",
         size=(400, 200),
         pos=(100, 100)
    )
    alert = Alert(surface, style)
    # Inside game loop
    if alert.visible:
         alert.update()
"""

import pygame

from dataclasses import dataclass
from typing import Optional, Literal, Dict

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg
from .button import ButtonText, StyleButton
from .textbox import TextBox, StyleTextBox

@dataclass(slots=True)
class StyleAlert:

    """
    Dataclass containing all visual and layout configuration for an Alert.

    Layout
    ------
    The alert is divided into two vertical sections:

    - Title frame  :
        Top portion, height = size[1] * per_height_title_frame

    - Content frame:
        Remaining portion, contains the wrapped text and close button

    Alert type
    ----------
    The `type` field controls the default title bar background color
    when `bg_title_color` is not explicitly set.

    Attributes
    ----------
    >>> title : str

        Text displayed in the title bar, centered vertically and horizontally.

    >>> title_color : ColorType

        Color of the title text.

    >>> content : str

        Body text displayed in the content area. Automatically word-wrapped.

    >>> text_color : ColorType

        Color of the content text.

    >>> line_height : int

        Additional spacing between lines in the content area.

    >>> type : Literal["error", "warning", "info", "success"]

        Alert variant. Controls the default title bar color.

    >>> bg_title_color : ColorType, optional

        Custom title bar background color.
        Overrides the type-based color if set.

    >>> bg_content_color : ColorType

        Background color of the content area.

    >>> size : Vec2

        Total size (width, height) of the alert box.

    >>> pos : Vec2

        Position (x, y) of the alert on the surface.

    >>> border : int

        Border thickness in pixels.
        0 means no border.

    >>> border_color : ColorType

        Color of the outer border.

    >>> padding : int

        Inner spacing between the content frame edge and the text.

    >>> per_height_title_frame : float

        Fraction of total height allocated to the title bar.
        Defaults to 0.20.

    >>> visible : bool

        Whether the alert is rendered.
        Defaults to True.

    >>> font : pygame.font.Font

        Font used for both the title and content text.

    >>> antialias : bool

        Whether to apply antialiasing to rendered text.
        Defaults to True.

    >>> button_color : ColorType

        Close button text color in normal state.

    >>> button_bg_color : ColorType

        Close button background color in normal state.

    >>> button_color_pressed : ColorType

        Close button text color when pressed.

    >>> button_bg_color_pressed : ColorType

        Close button background color when pressed.

    >>> button_color_hover : ColorType

        Close button text color when hovered.

    >>> button_bg_color_hover : ColorType

        Close button background color when hovered.
    """

    # general
    title: str = ""
    title_color: ColorType = "#222222"

    content: str = ""
    text_color: ColorType = "#222222"
    line_height: int = 0

    type: Literal["error", "warning", "info", "success"] = "info"

    bg_title_color: Optional[ColorType] = None
    bg_content_color: ColorType = "#f0f0f0"

    size: Vec2 = (500, 300)
    pos: Vec2 = (0, 0)

    border: int = 0
    border_color: ColorType = "#000000"

    padding: int = 0

    per_height_title_frame: float = 0.20

    visible: bool = True

    font: pygame.font.Font = pygame.font.Font(None, 25)

    antialias: bool = True

    # normal
    button_color: ColorType = "#333333"
    button_bg_color: ColorType = "#ffb3b3"

    # pressed
    button_color_pressed: ColorType = "#ffffff"
    button_bg_color_pressed: ColorType = "#ff884d"

    # hover
    button_color_hover: ColorType = "#ffffff"
    button_bg_color_hover: ColorType = "#ff884d"

class Alert:

    """
    A dismissible alert box component combining a title bar, content area,
    and a close button.

    The alert is split into two vertical sections — a colored title bar at the top
    and a text content area below. A close button is anchored to the right side
    of the title bar and hides the alert when clicked.

    The title bar color is determined by `StyleAlert.type` unless
    `StyleAlert.bg_title_color` is explicitly set.

    Layout (top to bottom)
    ----------------------
    1. Border
        Slightly larger rect behind the alert.

    2. Title frame
        Colored bar with centered title text and close button.

    3. Content frame
        TextBox with word-wrapped content text.

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which the alert is drawn.

    >>> style : StyleAlert

        The style/configuration object for this alert.

    Properties
    ----------
    >>> visible : bool

        Gets or sets whether the alert is rendered.

        Set to False automatically when the close button is clicked.

    Methods
    -------
    >>> update() -> None

        Draws the alert and updates the close button each frame.
        Does nothing if ``visible`` is False.

    >>> get_color_type() -> Dict[str, str]

        Returns the default color mapping for each alert type.

    Example
    -------
    >>> style = StyleAlert(
    ...     title="Warning",
    ...     content="Unsaved changes will be lost.",
    ...     type="warning",
    ...     size=(420, 220),
    ...     pos=(150, 150)
    ... )

    >>> alert = Alert(surface, style)

    >>> # Inside game loop
    >>> alert.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleAlert):
        self.__surface = surface
        self.__style = style

        self.__type_color = {
            "error": "#e74c3c",
            "wanring": "#f39c12",
            "success": "#27ae60",
            "info": "#3498db"
        }

        self.__visible = self.__style.visible

        self.__rect = pygame.Rect(self.__style.pos, self.__style.size)
        self.__rect_size = self.__rect.size

        self.__size_title_frame = (self.__rect_size[0], self.__rect_size[1] * self.__style.per_height_title_frame)
        self.__size_content_frame = (self.__rect_size[0], self.__rect_size[1] * (1 - self.__style.per_height_title_frame))

        self.__text_box = TextBox(
            self.__surface,
            StyleTextBox(
                content=self.__style.content,
                font=self.__style.font,
                color=self.__style.text_color,
                bg_color=self.__style.bg_content_color,
                antialias=self.__style.antialias,
                pos=(self.__style.pos[0], self.__style.pos[1] + self.__size_title_frame[1]),
                size=self.__size_content_frame,
                padding=self.__style.padding,
                line_height=self.__style.line_height
            )
        )

        fix_size_button = (5,5)
        self.__button_close = ButtonText(
            self.__surface,
            StyleButton(
                color=self.__style.button_color,
                color_hover=self.__style.button_color_hover,
                color_pressed=self.__style.button_color_pressed,
                bg_color=self.__style.button_bg_color,
                bg_color_hover=self.__style.button_bg_color_hover,
                bg_color_pressed=self.__style.button_bg_color_pressed,
                content="X",
                on_click=lambda: self.__close_alert(),
                size=to_array((self.__size_title_frame[1], self.__size_title_frame[1])) - 2 * to_array(fix_size_button),
                pos=to_array(self.__style.pos) + to_array((self.__size_title_frame[0] - self.__size_title_frame[1], 0)) + to_array(fix_size_button)
            )
        )
    
    def update(self):
        if self.__visible:
            self.__draw_border()
            self.__draw_title()
            self.__text_box.update()
            self.__button_close.update()
    
    @property
    def visible(self) -> bool: 
        return self.__visible
    
    @visible.setter
    def visible(self, new_visible: bool) -> None:
        self.__visible = new_visible

    def get_color_type(self) -> Dict[str, str]:
        return self.__type_color
    
    def __draw_title(self) -> None:
        title_frame = pygame.Rect(self.__style.pos, self.__size_title_frame)

        title_surface = self.__style.font.render(self.__style.title, self.__style.antialias, self.__style.title_color)
        title_rect = title_surface.get_rect(center=title_frame.center)

        pygame.draw.rect(self.__surface,
                         hex_to_rbg(self.__style.bg_title_color if self.__style.bg_title_color is not None else self.__type_color[self.__style.type]),
                         title_frame)
        
        self.__surface.blit(title_surface, title_rect)
    
    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        size_border: Vec2 = to_array(self.__style.size) + to_array(border_width) * 2
        pos: Vec2 = to_array(self.__style.pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos[0]), int(pos[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border)
    
    def __close_alert(self) -> None:
        self.visible = False