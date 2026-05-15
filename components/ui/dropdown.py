"""
Dropdown Module
===============
This module provides a dropdown selection UI component built on top of pygame,
using ButtonText internally to render each selectable option in the list.

The dropdown consists of a clickable header that toggles
an option list open or closed.

Selecting an item updates the header label
and closes the list automatically.

It includes:
- `StateDropdown`  : Enum defining the visual states of the dropdown header.
- `StyleDropdown`  : Dataclass holding all style/configuration options for a dropdown.
- `Dropdown`       : Renders an interactive dropdown with a header
                     and collapsible option list.

Typical usage:
>>> style = StyleDropdown(
        options=["Option A", "Option B", "Option C"],
        selected_index=0,
        size=(200, 40),
        pos=(100, 100)
    )
    dropdown = Dropdown(surface, style)
    # Inside game loop
    dropdown.update()
    # Read current selection
    value = dropdown.get_selected_item()
"""

import pygame

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

from utils.utils_typing import Vec2, ColorType
from utils.utils_transform import to_array, hex_to_rbg

from .button import StyleButton, ButtonText

class StateDropdown(Enum):

    """
    Enum representing the visual states of the Dropdown header.

    States
    ------
    >>> NORMAL : int

        Default state — no interaction is occurring.

    >>> HOVER : int

        The mouse cursor is hovering over the header.

    >>> PRESSED : int

        The header is currently being held down by the mouse.

    >>> OPEN : int

        The dropdown list is currently open and visible.
        Takes visual priority over all other states.
"""

    NORMAL = 1
    HOVER = 2
    PRESSED = 3
    OPEN = 4

@dataclass(slots=True)
class StyleDropdown:

    """
    Dataclass containing all visual and behavioral configuration
    for a Dropdown.

    Layout
    ------
    The dropdown is divided into two parts:

    - Header : always visible,
            shows the selected item or placeholder text.

    - List   : shown below the header when open,
            contains all selectable options.

    State-based styling
    -------------------
    The header supports four visual states:
    normal, hover, pressed, and open.

    Each option item supports four states:
    normal, hover, pressed, and selected.

    The selected state takes priority over all others
    for the active item.

    Attributes
    ----------
    >>> options : List[str]

        The list of selectable option labels.

    >>> selected_index : int

        Index of the initially selected option.
        Defaults to 0.

    >>> placeholder : str

        Text shown in the header when no option
        is selected or options is empty.

    >>> size : Vec2

        Size (width, height) of the header
        and each option item.

    >>> pos : Vec2

        Position (x, y) of the dropdown header
        on the surface.

    >>> padding : int

        Inner horizontal spacing between
        the header edge and the label text.

    >>> gap : int

        Vertical spacing between each option item
        in the list.

    >>> border : int

        Border thickness in pixels.
        Defaults to 1.

    >>> border_radius : int

        Corner radius for rounded borders.
        Defaults to 0.

    >>> font : pygame.font.Font

        Font used for the header label
        and all option items.

    >>> antialias : bool

        Whether to apply antialiasing
        to rendered text.
        Defaults to True.

    >>> visible : bool

        Whether the dropdown is rendered
        and interactive.
        Defaults to True.

    >>> on_sound_open : pygame.mixer.Sound, optional

        Sound played when the dropdown
        is toggled open or closed.

    >>> on_sound_select : pygame.mixer.Sound, optional

        Sound played when an option is selected.

    Header states
    -------------
    >>> header_color

        Header label text color in normal state.

    >>> header_color_hover

        Header label text color when hovered.

    >>> header_color_pressed

        Header label text color when pressed.

    >>> header_color_open

        Header label text color when open.

    >>> header_bg_color

        Header background color in normal state.

    >>> header_bg_color_hover

        Header background color when hovered.

    >>> header_bg_color_pressed

        Header background color when pressed.

    >>> header_bg_color_open

        Header background color when open.

    >>> header_border_color

        Header border color in normal state.

    >>> header_border_color_hover

        Header border color when hovered.

    >>> header_border_color_pressed

        Header border color when pressed.

    >>> header_border_color_open

        Header border color when open.

    Item states
    -----------
    >>> item_color

        Option item text color in normal state.

    >>> item_color_hover

        Option item text color when hovered.

    >>> item_color_pressed

        Option item text color when pressed.

    >>> item_color_selected

        Option item text color when selected.

    >>> item_bg_color

        Option item background color in normal state.

    >>> item_bg_color_hover

        Option item background color when hovered.

    >>> item_bg_color_pressed

        Option item background color when pressed.

    >>> item_bg_color_selected

        Option item background color when selected.
    """

    # content
    options: List[str] = field(default_factory=list)
    selected_index: int = 0
    placeholder: str = "Select..."

    # layout
    size: Vec2 = (200, 40)
    pos: Vec2 = (0, 0)
    padding: int = 8
    gap: int = 1

    # border
    border: int = 1
    border_radius: int = 0

    # font
    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(None, 25))
    antialias: bool = True

    # general
    visible: bool = True
    on_sound_open: Optional[pygame.mixer.Sound] = None
    on_sound_select: Optional[pygame.mixer.Sound] = None

    # header normal
    header_color: ColorType = "#222222"
    header_bg_color: ColorType = "#ffffff"
    header_border_color: ColorType = "#aaaaaa"

    # header hover
    header_color_hover: ColorType = "#222222"
    header_bg_color_hover: ColorType = "#f0f0f0"
    header_border_color_hover: ColorType = "#aaaaaa"

    # header pressed
    header_color_pressed: ColorType = "#222222"
    header_bg_color_pressed: ColorType = "#f0f0f0"
    header_border_color_pressed: ColorType = "#aaaaaa"

    # header open
    header_color_open: ColorType = "#222222"
    header_bg_color_open: ColorType = "#e8e8e8"
    header_border_color_open: ColorType = "#aaaaaa"

    # item normal
    item_color: ColorType = "#222222"
    item_bg_color: ColorType = "#ffffff"

    # item hover
    item_color_hover: ColorType = "#222222"
    item_bg_color_hover: ColorType = "#e8f0fe"

    # item pressed
    item_color_pressed: ColorType = "#222222"
    item_bg_color_pressed: ColorType = "#e8f0fe"

    # item selected
    item_color_selected: ColorType = "#ffffff"
    item_bg_color_selected: ColorType = "#4caf50"

class Dropdown:

    """
    An interactive dropdown component
    with a toggleable option list.

    Clicking the header opens or closes
    the option list.

    Clicking an option selects it,
    updates the header label,
    and closes the list.

    The header and each option item update
    their colors based on the current visual state.

    Rendering order (back to front)
    --------------------------------
    1. Header border
    (slightly larger rect behind the header)

    2. Header background

    3. Header label
    (selected item or placeholder,
    left-aligned with padding)

    4. Option list
    (rendered below the header,
    one ButtonText per item)

    State priority
    --------------
    OPEN state overrides hover and pressed
    for the header, ensuring the open appearance
    is visually distinct from interaction states.

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which the dropdown is drawn.

    >>> style : StyleDropdown

        The style/configuration object
        for this dropdown.

    Methods
    -------
    >>> update() -> None

        Handles mouse interaction,
        toggles the list open/closed,
        and renders the header and option list
        each frame.
        Does nothing if ``StyleDropdown.visible`` is False.

    >>> get_selected_item() -> str

        Returns the string value
        of the currently selected option.

    Example
    -------
>>> style = StyleDropdown(
            options=["Easy", "Medium", "Hard"],
            selected_index=1,
            size=(200, 40),
            pos=(100, 200)
        )
        dropdown = Dropdown(surface, style)
        # Inside game loop
        dropdown.update()
        # Read selection
        difficulty = dropdown.get_selected_item()
        # -> "Medium"
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleDropdown):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos 

        self.__is_open = False
        self.__is_hover_header = False
        self.__is_pressed_header = False

        self.__header = pygame.Rect(self.__pos, self.__style.size)

        self.__active_index = self.__style.selected_index

        self.__placeholder = self.__style.placeholder if not self.__style.options else self.__style.options[self.__active_index]

        self.__list_options = self.__create_list_options()
    
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
            mouse_pos = pygame.mouse.get_pos()
            self.__is_hover_header = self.__header.collidepoint(mouse_pos)
            
            if self.__is_hover_header and pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed_header: 
                    self.__is_pressed_header = True
                    self.__is_open = not self.__is_open
            else:
                if self.__is_pressed_header and self.__is_hover_header:
                    if self.__style.on_sound_open is not None: self.__style.on_sound_open.play()
                self.__is_pressed_header = False
                    
            visual_state_header = self.__get_visual_state_header()

            color_header = self.__get_color_state_header(visual_state_header)
            bg_color = self.__get_bg_color_state_header(visual_state_header)
            border_color = self.__get_border_color_state_header(visual_state_header)

            self.__draw_border_header(border_color)
            self.__draw_bg_header(bg_color)
            self.__draw_content_header(color_header)

            if self.__is_open:
                self.__draw_list_options()
    
    def get_selected_item(self) -> str:
        return self.__style.options[self.__active_index]
    
    def __create_list_options(self) -> List[ButtonText]:
        list_options: List[ButtonText] = []

        for index, label in enumerate(self.__style.options):
            pos_option = to_array(self.__pos) + to_array((0, self.__style.size[1])) * index + to_array((0, self.__style.gap + self.__style.size[1]))

            option = ButtonText(
                surface=self.__surface,
                style=StyleButton(
                    color=self.__style.item_color if index != self.__active_index else self.__style.item_color_selected,
                    color_hover=self.__style.item_color_hover,
                    color_pressed=self.__style.item_color_pressed,
                    bg_color=self.__style.item_bg_color if index != self.__active_index else self.__style.item_bg_color_selected,
                    bg_color_hover=self.__style.item_bg_color_hover,
                    bg_color_pressed=self.__style.item_bg_color_pressed,
                    content=label,
                    font=self.__style.font,
                    antialias=self.__style.antialias,
                    on_click=lambda i = index: self.__change_selected_index(i),
                    on_sound=self.__style.on_sound_select,
                    size=self.__style.size,
                    pos=(int(pos_option[0]), int(pos_option[1]))
                )
            )

            list_options.append(option)

        return list_options

    def __get_color_state_header(self, state: StateDropdown) -> ColorType:
        if state == StateDropdown.HOVER: color = self.__style.header_color_hover
        elif state == StateDropdown.PRESSED: color = self.__style.header_color_pressed
        elif state == StateDropdown.OPEN: color = self.__style.header_color_open
        else: color = self.__style.header_color

        return hex_to_rbg(color)
    
    def __get_bg_color_state_header(self, state: StateDropdown) -> ColorType:
        if state == StateDropdown.HOVER: color = self.__style.header_bg_color_hover
        elif state == StateDropdown.PRESSED: color = self.__style.header_bg_color_pressed
        elif state == StateDropdown.OPEN: color = self.__style.header_bg_color_open
        else: color = self.__style.header_bg_color

        return hex_to_rbg(color)
    
    def __get_border_color_state_header(self, state: StateDropdown) -> ColorType:
        if state == StateDropdown.HOVER: color = self.__style.header_border_color_hover
        elif state == StateDropdown.PRESSED: color = self.__style.header_border_color_pressed
        elif state == StateDropdown.OPEN: color = self.__style.header_border_color_open
        else: color = self.__style.header_border_color

        return hex_to_rbg(color)
    
    def __get_visual_state_header(self) -> StateDropdown:
        if self.__is_open: return StateDropdown.OPEN
        elif self.__is_hover_header: return StateDropdown.HOVER
        elif self.__is_pressed_header: return StateDropdown.PRESSED
        return StateDropdown.NORMAL

    def __draw_bg_header(self, color: ColorType) -> None:
        header = self.__header
        pygame.draw.rect(self.__surface, color, header, border_radius=self.__style.border_radius)
    
    def __draw_border_header(self, color: ColorType) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2
        pos_border = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, color, border, border_radius=self.__style.border_radius)
    
    def __draw_content_header(self, color: ColorType) -> None:
        text_surface = self.__style.font.render(self.__placeholder, self.__style.antialias,  color)
        text_rect = text_surface.get_rect(midleft=self.__header.midleft)
        text_rect[0] += self.__style.padding

        self.__surface.blit(text_surface, text_rect)
    
    def __draw_list_options(self) -> None:
        for option in self.__list_options:
            option.update()
    
    def __change_selected_index(self, index: int) -> None:
        if index < 0 or index > len(self.__style.options): return
        if index == self.__active_index: return

        self.__active_index = index
        self.__placeholder = self.__style.options[index]

        self.__list_options = self.__create_list_options()

        self.__is_open = False

