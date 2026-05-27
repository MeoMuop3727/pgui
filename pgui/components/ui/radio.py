"""
RadioButton Module
==================
This module provides a radio button and radio button list UI component built on top of pygame.
Unlike checkboxes, only one radio button in a group can be active at a time —
selecting one automatically deselects all others in the same list.

It includes:
- `StateRadioButton`  : Enum defining the visual states of a radio button.
- `StyleRadioButton`  : Dataclass holding all style/configuration options for a radio button.
- `RadioButton`       : Renders a single interactive radio button with a text label.
- `RadioButtonList`   : Manages a vertical list of radio buttons with exclusive selection logic.

Typical usage:
>>> style = StyleRadioButton(
        label_list=["Option A", "Option B", "Option C"],
        checked_list=[True, False, False],
        on_change=lambda states: print(states)
    )
    radio_list = RadioButtonList(surface, style)
    # Inside game loop
    radio_list.update()
    # Read current states
    states = radio_list.get_state_radio_button()
"""

import pygame

from dataclasses import dataclass, field
from typing import Optional, Callable, List
from enum import Enum

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import to_array, hex_to_rbg

class StateRadioButton(Enum):

    """
    Enum representing the visual states of a RadioButton.

    States
    ------
    NORMAL : int
        Default state — no interaction is occurring.
    HOVER : int
        The mouse cursor is hovering over the radio button.
    PRESSED : int
        The radio button is currently being held down by the mouse.

    Note
    ----
    The checked (selected) state is tracked separately via
    ``RadioButton.__is_checked`` and overlays the visual state when active.
    """

    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleRadioButton:

    """
    Dataclass containing all visual and behavioral configuration
    for a RadioButton or RadioButtonList.

    State-based styling
    -------------------
    Each visual property (bg_color, border_color, label_color) has four variants
    corresponding to the interaction state: normal, hover, pressed, and checked.
    The checked state takes priority over all other states when the button is selected.

    Attributes
    ----------
    label_list : List[str]
        List of label strings, one per radio button (used by RadioButtonList).
    size : Vec2
        Overall size (width, height) reserved for the component.
    pos : Vec2
        Position (x, y) of the first radio button on the surface.
    border : int
        Border thickness in pixels. Defaults to 1.
    border_radius : int
        Corner radius for the button border. Defaults to 50 (circle shape).
    border_color : ColorType
        Border color in normal state.
    gap : int
        Horizontal spacing between the button and its label. Defaults to 8.
    line_height : int
        Additional vertical spacing between buttons in a list. Defaults to 5.
    font : pygame.font.Font
        Font used to render button labels.
    antialias : bool
        Whether to apply antialiasing to rendered labels. Defaults to True.
    visible : bool
        Whether the component is rendered and interactive. Defaults to True.
    on_change : Callable[[List[bool]], None], optional
        Callback triggered when the selected radio button changes.
        Receives the updated list of checked states.
    on_sound : pygame.mixer.Sound, optional
        Sound played when a radio button is selected.
    checked_list : List[bool]
        Initial checked state for each radio button in the list.

    Normal state
    ------------
    bg_color : ColorType
        Background color in normal state. Defaults to #ffffff.
    check_color : ColorType
        Inner indicator color in normal state. Defaults to #333333.
    label_color : ColorType
        Label text color in normal state. Defaults to #222222.

    Hover state
    -----------
    bg_color_hover : ColorType
        Background color when hovered. Defaults to #f0f0f0.
    border_color_hover : ColorType
        Border color when hovered. Defaults to #888888.
    label_color_hover : ColorType
        Label color when hovered. Defaults to #222222.

    Pressed state
    -------------
    bg_color_pressed : ColorType
        Background color when pressed. Defaults to #e0e0e0.
    border_color_pressed : ColorType
        Border color when pressed. Defaults to #555555.
    label_color_pressed : ColorType
        Label color when pressed. Defaults to #222222.

    Checked state
    -------------
    bg_color_checked : ColorType
        Background color when selected. Defaults to #4caf50.
    border_color_checked : ColorType
        Border color when selected. Defaults to #388e3c.
    label_color_checked : ColorType
        Label color when selected. Defaults to #222222.
    """
    
    # general
    label_list: List[str] = field(default_factory=list)
    size: Vec2 = (200, 40)
    pos: Vec2 = (0, 0)

    border: int = 1
    border_radius: int = 50
    border_color: ColorType = "#aaaaaa"

    gap: int = 8
    line_height: int = 5

    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(None, 25))

    antialias: bool = True
    visible: bool = True

    on_change: Optional[Callable[[Optional[List[bool]]], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

    checked_list: List[bool] = field(default_factory=list)

    # normal
    bg_color: ColorType = "#ffffff"
    check_color: ColorType = "#333333"
    border_color: ColorType = "#aaaaaa"
    label_color: ColorType = "#222222"

    # hover
    bg_color_hover: ColorType = "#f0f0f0"
    border_color_hover: ColorType = "#888888"
    label_color_hover: ColorType = "#222222"

    # pressed
    bg_color_pressed: ColorType = "#e0e0e0"
    border_color_pressed: ColorType = "#555555"
    label_color_pressed: ColorType = "#222222"

    # checked
    bg_color_checked: ColorType = "#4caf50"
    border_color_checked: ColorType = "#388e3c"
    label_color_checked: ColorType = "#222222"

class RadioButton:

    """
    A single interactive radio button that renders a clickable circular button
    and a text label beside it.

    Clicking the button sets it to checked. Once checked, it cannot be unchecked
    by clicking again — only ``RadioButtonList`` can uncheck it by selecting another
    button in the group.

    Rendering order (back to front)
    --------------------------------
    1. Border   (slightly larger rect behind the button)
    2. Button   (the main circular button)
    3. Label    (text rendered to the right, offset by gap)

    State priority
    --------------
    Checked state overrides hover and pressed colors,
    ensuring the selected appearance is always visually distinct.

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which the radio button is drawn.

>>> style : StyleRadioButton

        The shared style/configuration object.

>>> pos : Vec2

        Position (x, y) of this specific radio button on the surface.

>>> label : str

        Text label displayed beside the radio button.

>>> checked : bool

        Initial checked state of this radio button.

    Properties
    ----------
>>> checked : bool

        Gets or sets the current checked state of the radio button.
        Used by ``RadioButtonList`` to enforce exclusive selection.

    Methods
    -------
>>> update() -> None

        Handles mouse interaction, updates checked state on click,
        and renders the radio button each frame.
        Does nothing if ``StyleRadioButton.visible`` is False.
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleRadioButton,
                 pos: Vec2 = (0,0),
                 label: str = "",
                 checked: bool = False):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos 

        self.__pos = pos
        self.__label = label

        self.__is_hovered = False
        self.__is_pressed = False
        self.__is_checked = checked

        self.__size_radio_button: Vec2 = (self.__style.font.get_height(), self.__style.font.get_height())
        self.__rect = pygame.Rect(self.__pos, self.__size_radio_button)
    
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
            self.__is_hover = self.__rect.collidepoint(mouse_pos)
            
            if self.__is_hover and pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed: 
                    self.__is_pressed = True
                    if not self.__is_checked: self.__is_checked = True
            else:
                if self.__is_pressed and self.__is_hover:
                    if self.__style.on_change is not None and self.__is_checked: self.__style.on_change()
                    if self.__style.on_sound is not None: self.__style.on_sound.play()
                self.__is_pressed = False
                        
            visual_state = self.__get_visual_state()

            bg_radio_button = self.__get_bg_color_state(visual_state)
            label_color = self.__get_label_color_state(visual_state)
            border_color = self.__get_border_color_state(visual_state)

            self.__draw_border_radio_button(border_color)
            self.__draw_bg_radio_button(bg_radio_button)
            self.__draw_label(self.__label, label_color)

    @property
    def checked(self) -> bool:
        return self.__is_checked
    
    @checked.setter
    def checked(self, state: bool) -> None:
        self.__is_checked = state

    def __get_visual_state(self) -> StateRadioButton:
        if self.__is_pressed: return StateRadioButton.PRESSED
        elif self.__is_hovered: return StateRadioButton.HOVER
        return StateRadioButton.NORMAL
    
    def __get_bg_color_state(self, state: StateRadioButton):
        if state == StateRadioButton.PRESSED: color = self.__style.bg_color_pressed
        elif state == StateRadioButton.HOVER: color = self.__style.bg_color_hover
        else: color = self.__style.bg_color

        if self.__is_checked: color = self.__style.bg_color_checked

        return hex_to_rbg(color)
    
    def __get_border_color_state(self, state: StateRadioButton):
        if state == StateRadioButton.PRESSED: color = self.__style.border_color_pressed
        elif state == StateRadioButton.HOVER: color = self.__style.border_color_hover
        else: color = self.__style.border_color

        if self.__is_checked: color = self.__style.border_color_checked

        return hex_to_rbg(color)
    
    def __get_label_color_state(self, state: StateRadioButton):
        if state == StateRadioButton.PRESSED: color = self.__style.label_color_pressed
        elif state == StateRadioButton.HOVER: color = self.__style.label_color_hover
        else: color = self.__style.label_color

        if self.__is_checked: color = self.__style.label_color_checked

        return hex_to_rbg(color)

    def __draw_bg_radio_button(self, color: ColorType) -> None:
        radio_button = self.__rect
        pygame.draw.rect(self.__surface, color, radio_button, border_radius=self.__style.border_radius)

    def __draw_border_radio_button(self, color: ColorType) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__size_radio_button) + to_array(border_width) * 2
        pos_border = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, color, border, border_radius=self.__style.border_radius)

    def __draw_label(self, label: str, color: ColorType) -> None:
        text_surface = self.__style.font.render(label, self.__style.antialias, color)
        text_rect = to_array(self.__pos) + to_array((self.__style.gap, 0)) + to_array((self.__size_radio_button[0], 0)) + to_array((self.__style.border, 0))

        self.__surface.blit(text_surface, text_rect)

class RadioButtonList:

    """
    A vertical list of radio buttons with exclusive selection logic.

    Only one radio button in the list can be checked at a time.
    When a new button is selected, all others are automatically unchecked.
    The active index is tracked internally and updated on each selection change.

    Attributes
    ----------
>>> surface : pygame.Surface
    
        The surface on which all radio buttons are drawn.
    
>>> style : StyleRadioButton
    
        The style/configuration object defining labels, colors, and layout.

    Methods
    -------
>>> update() -> None

        Enforces exclusive selection, then updates and renders all
        radio buttons each frame.
        Does nothing if ``StyleRadioButton.visible`` is False.

>>> get_state_radio_button() -> List[bool]

        Returns a list of checked states for all radio buttons,
        in the same order as ``StyleRadioButton.label_list``.
        Only one value will be True at any given time.

    Example
    -------
>>> style = StyleRadioButton(
            label_list=["Small", "Medium", "Large"],
            checked_list=[False, True, False],
            pos=(50, 100),
            on_change=lambda states: print(states)
        ) 
        radio_list = RadioButtonList(surface, style)
        # Inside game loop
        radio_list.update()
        # Read active selection
        states = radio_list.get_state_radio_button()
        # -> [False, True, False]
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleRadioButton):
        self.__surface = surface
        self.__style = style

        self.__list_radio_button: List[RadioButton] = self.__create_list_radio_button()
        self.__active_index = self.__get_default_active_index()
    
    def update(self) -> None:
        if self.__style.visible:
            self.__handle_exclusive_selec()
            self.__draw_radio_button()
    
    def get_state_radio_button(self) -> List[bool]:
        return [radio_button.checked for radio_button in self.__list_radio_button]

    def __draw_radio_button(self) -> None:
        if self.__list_radio_button:
            for radio_button in self.__list_radio_button:
                radio_button.update()
    
    def __create_list_radio_button(self) -> List[RadioButton]:
        list_radio_button: List[RadioButton] = []

        for index, label in enumerate(self.__style.label_list):
            index_checked = index if index < len(self.__style.checked_list) else 0

            pos_radio_button = to_array(self.__pos) + (to_array((0, self.__style.font.get_height())) + to_array((0, self.__style.line_height))) * index

            radio_button = RadioButton(
                surface=self.__surface,
                style=self.__style,
                pos=(int(pos_radio_button[0]), int(pos_radio_button[1])),
                label=label,
                checked=index_checked
            )

            list_radio_button.append(radio_button)
        return list_radio_button
    
    def __handle_exclusive_selec(self) -> None:
        for index, radio_button in enumerate(self.__list_radio_button):
            if radio_button.checked and index != self.__active_index:
                self.__active_index = index
                self.__uncheck_all_except(index)

                if self.__style.on_change is not None:
                    self.__style.on_change(self.get_state_radio_button())
                if self.__style.on_sound is not None:
                    self.__style.on_sound.play()
                break

    def __uncheck_all_except(self, active_index: int) -> None:
        for index, radio_button in enumerate(self.__list_radio_button):
            if index != active_index:
                radio_button.checked = False
    
    def __get_default_active_index(self) -> int:
        for index, radio_button in enumerate(self.__list_radio_button):
            if radio_button.checked:
                return index
        return -1
