"""
Checkbox Module
===============
This module provides a checkbox and checkbox list UI component built on top of pygame.
Each checkbox renders a clickable box, a visual checkmark when active, and a text label.
Multiple checkboxes can be grouped and managed together via CheckBoxList.

It includes:
- `StateCheckbox`  : Enum defining the visual states of a checkbox.
- `StyleCheckBox`  : Dataclass holding all style/configuration options for a checkbox.
- `CheckBox`       : Renders a single interactive checkbox with label.
- `CheckBoxList`   : Manages and renders a vertical list of checkboxes from a label list.

Typical usage:
>>> style = StyleCheckBox(
         label_list=["Option A", "Option B", "Option C"],
         checked_list=[True, False, False],
         on_change=lambda states: print(states)
     )
     checkbox_list = CheckBoxList(surface, style)
     # Inside game loop
     checkbox_list.update()
     # Read current states
     states = checkbox_list.get_state_check_boxes()
"""

import pygame

from dataclasses import dataclass, field
from typing import Optional, Callable, List
from enum import Enum

from utils.utils_typing import Vec2, ColorType
from utils.utils_transform import to_array, hex_to_rbg

class StateCheckbox(Enum):

    """
    Enum representing the visual states of a CheckBox.

    States
    ------
    >>> NORMAL : int

        Default state — no interaction is occurring.

    >>> HOVER : int

        The mouse cursor is hovering over the checkbox.

    >>> PRESSED : int

        The checkbox is currently being held down by the mouse.

    Note
    ----
    The checked (ON/OFF) state is tracked separately via
    ``CheckBox.__is_checked`` and overlays the visual state when active.
    """

    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleCheckBox:

    """
    Dataclass containing all visual and behavioral configuration
    for a CheckBox or CheckBoxList.

    State-based styling
    -------------------
    Each visual property (bg_color, border_color, label_color)
    has four variants corresponding to the interaction state:
    normal, hover, pressed, and checked.

    The checked state takes priority over all other states
    when the box is ticked.

    Attributes
    ----------
    >>> label_list : List[str]

        List of label strings, one per checkbox
        (used by CheckBoxList).

    >>> size : Vec2

        Overall size (width, height) reserved
        for the checkbox component.

    >>> pos : Vec2

        Position (x, y) of the first checkbox
        on the surface.

    >>> border : int

        Border thickness in pixels.
        Defaults to 1.

    >>> border_radius : int

        Corner radius for rounded box borders.
        Defaults to 0.

    >>> border_color : ColorType

        Border color in normal state.

    >>> gap : int

        Horizontal spacing between the box
        and its label.
        Defaults to 8.

    >>> line_height : int

        Additional vertical spacing between
        checkboxes in a list.
        Defaults to 5.

    >>> font : pygame.font.Font

        Font used to render checkbox labels.

    >>> antialias : bool

        Whether to apply antialiasing
        to rendered labels.
        Defaults to True.

    >>> visible : bool

        Whether the checkbox is rendered
        and interactive.
        Defaults to True.

    >>> checked_list : List[bool]

        Initial checked state for each
        checkbox in a list.

    >>> on_change : Callable[[List[bool]], None], optional

        Callback triggered when any checkbox
        state changes.
        Receives the updated list
        of checked states.

    >>> on_sound : pygame.mixer.Sound, optional

        Sound played when a checkbox is toggled.

    Normal state
    ------------
    >>> bg_color : ColorType

        Background color in normal state.
        Defaults to #ffffff.

    >>> check_color : ColorType

        Checkmark color in normal state.
        Defaults to #333333.

    >>> label_color : ColorType

        Label text color in normal state.
        Defaults to #222222.

    Hover state
    -----------
    >>> bg_color_hover : ColorType

        Background color when hovered.
        Defaults to #f0f0f0.

    >>> border_color_hover : ColorType

        Border color when hovered.
        Defaults to #888888.

    >>> label_color_hover : ColorType

        Label color when hovered.
        Defaults to #222222.

    Pressed state
    -------------
    >>> bg_color_pressed : ColorType

        Background color when pressed.
        Defaults to #e0e0e0.

    >>> border_color_pressed : ColorType

        Border color when pressed.
        Defaults to #555555.

    >>> label_color_pressed : ColorType

        Label color when pressed.
        Defaults to #222222.

    Checked state
    -------------
    >>> bg_color_checked : ColorType

        Background color when checked.
        Defaults to #4caf50.

    >>> border_color_checked : ColorType

        Border color when checked.
        Defaults to #388e3c.

    >>> label_color_checked : ColorType

        Label color when checked.
        Defaults to #222222.
    """

    # general
    label_list: List[str] = field(default_factory=list)
    size: Vec2 = (200, 40)
    pos: Vec2 = (0, 0)

    border: int = 1
    border_radius: int = 0
    border_color: ColorType = "#aaaaaa"

    gap: int = 8
    line_height: int = 5

    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(None, 25))

    antialias: bool = True
    visible: bool = True

    checked_list: List[bool] = field(default_factory=list)

    on_change: Optional[Callable[[Optional[List[bool]]], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

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

class CheckBox:

    """
    A single interactive checkbox that renders a clickable box
    and a text label.

    Clicking the box toggles its checked state.
    Colors for the background, border, and label all update
    based on the current interaction and checked state.

    The checked state takes visual priority over
    hover and pressed states.

    Rendering order (back to front)
    --------------------------------
    1. Border   (slightly larger rect behind the box)
    2. Box      (the main checkbox square)
    3. Label    (text rendered to the right of the box)

    State priority
    --------------
    Checked state overrides hover and pressed colors,
    ensuring the checked appearance is always visually distinct.

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which the checkbox is drawn.

    >>> style : StyleCheckBox

        The shared style/configuration object.

    >>> pos : Vec2

        Position (x, y) of this specific checkbox
        on the surface.

    >>> label : str

        Text label displayed beside the checkbox box.

    >>> checked : bool

        Initial checked state of this checkbox.

    Properties
    ----------
    >>> checked : bool

        Returns the current checked state
        of the checkbox.

    Methods
    -------
    >>> update() -> None

        Handles mouse interaction,
        toggles checked state on click,
        and renders the checkbox each frame.
        Does nothing if
        ``StyleCheckBox.visible`` is False.
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleCheckBox,
                 pos: Vec2 = (0,0),
                 label: str = "",
                 checked: bool = False):
        self.__surface = surface
        self.__style = style

        self.__pos = pos
        self.__label = label

        self.__is_hovered = False
        self.__is_pressed = False
        self.__is_checked = checked

        self.__size_check_box: Vec2 = (self.__style.font.get_height(), self.__style.font.get_height())
        self.__rect = pygame.Rect(self.__pos, self.__size_check_box)
    
    def update(self) -> None:
        if self.__style.visible:
            mouse_pos = pygame.mouse.get_pos()
            self.__is_hover = self.__rect.collidepoint(mouse_pos)
            
            if self.__is_hover and pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed: 
                    self.__is_pressed = True
                    self.__is_checked = not self.__is_checked
            else:
                if self.__is_pressed and self.__is_hover:
                    if self.__style.on_change is not None and self.__is_checked: self.__style.on_change()
                    if self.__style.on_sound is not None: self.__style.on_sound.play()
                self.__is_pressed = False
                        
            visual_state = self.__get_visual_state()

            bg_check_box = self.__get_bg_color_state(visual_state)
            label_color = self.__get_label_color_state(visual_state)
            border_color = self.__get_border_color_state(visual_state)

            self.__draw_border_check_box(border_color)
            self.__draw_bg_check_box(bg_check_box)
            self.__draw_label(self.__label, label_color)

    @property
    def checked(self) -> bool:
        return self.__is_checked

    def __get_visual_state(self) -> StateCheckbox:
        if self.__is_pressed: return StateCheckbox.PRESSED
        elif self.__is_hovered: return StateCheckbox.HOVER
        return StateCheckbox.NORMAL
    
    def __get_bg_color_state(self, state: StateCheckbox):
        if state == StateCheckbox.PRESSED: color = self.__style.bg_color_pressed
        elif state == StateCheckbox.HOVER: color = self.__style.bg_color_hover
        else: color = self.__style.bg_color

        if self.__is_checked: color = self.__style.bg_color_checked

        return hex_to_rbg(color)
    
    def __get_border_color_state(self, state: StateCheckbox):
        if state == StateCheckbox.PRESSED: color = self.__style.border_color_pressed
        elif state == StateCheckbox.HOVER: color = self.__style.border_color_hover
        else: color = self.__style.border_color

        if self.__is_checked: color = self.__style.border_color_checked

        return hex_to_rbg(color)
    
    def __get_label_color_state(self, state: StateCheckbox):
        if state == StateCheckbox.PRESSED: color = self.__style.label_color_pressed
        elif state == StateCheckbox.HOVER: color = self.__style.label_color_hover
        else: color = self.__style.label_color

        if self.__is_checked: color = self.__style.label_color_checked

        return hex_to_rbg(color)

    def __draw_bg_check_box(self, color: ColorType) -> None:
        check_box = self.__rect
        pygame.draw.rect(self.__surface, color, check_box, border_radius=self.__style.border_radius)

    def __draw_border_check_box(self, color: ColorType) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__size_check_box) + to_array(border_width) * 2
        pos_border = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, color, border, border_radius=self.__style.border_radius)

    def __draw_label(self, label: str, color: ColorType) -> None:
        text_surface = self.__style.font.render(label, self.__style.antialias, color)
        text_rect = to_array(self.__pos) + to_array((self.__style.gap, 0)) + to_array((self.__size_check_box[0], 0)) + to_array((self.__style.border, 0))

        self.__surface.blit(text_surface, text_rect)

class CheckBoxList:

    """
    A vertical list of checkboxes generated from
    ``StyleCheckBox.label_list``.

    Each label in the list becomes a separate
    ``CheckBox`` instance spaced vertically
    based on font height and line_height.

    All checkboxes share the same style configuration.

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which all checkboxes are drawn.

    >>> style : StyleCheckBox

        The style/configuration object defining
        labels, colors, and layout.

    Methods
    -------
    >>> update() -> None

        Updates and renders all checkboxes each frame.
        Does nothing if
        ``StyleCheckBox.visible`` is False.

    >>> get_state_check_boxes() -> List[bool]

        Returns a list of checked states
        for all checkboxes in the same order as
        ``StyleCheckBox.label_list``.

    Example
    -------
>>> style = StyleCheckBox(
            label_list=[
                "Enable sound",
                "Show FPS",
                "Fullscreen"
            ],
            checked_list=[True, False, False],
            pos=(50, 100)
        )
        cb_list = CheckBoxList(surface, style)
        # Inside game loop
        cb_list.update()
        # Read states
        states = cb_list.get_state_check_boxes()
        # -> [True, False, False]
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleCheckBox):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible

        self.__list_check_box: List[CheckBox] = self.__create_list_check_box()
    
    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value
    
    def update(self) -> None:
        if self.__visible:
            self.__draw_check_box()
    
    def get_state_check_boxes(self) -> List[bool]:
        return [check_box.checked for check_box in self.__list_check_box]

    def __draw_check_box(self) -> None:
        if self.__list_check_box:
            for check_box in self.__list_check_box:
                check_box.update()
    
    def __create_list_check_box(self) -> List[CheckBox]:
        list_check_box: List[CheckBox] = []

        for index, label in enumerate(self.__style.label_list):
            index_checked = index if index < len(self.__style.checked_list) else 0

            pos_check_box = to_array(self.__style.pos) + (to_array((0, self.__style.font.get_height())) + to_array((0, self.__style.line_height))) * index

            check_box = CheckBox(
                surface=self.__surface,
                style=self.__style,
                pos=(int(pos_check_box[0]), int(pos_check_box[1])),
                label=label,
                checked=index_checked
            )

            list_check_box.append(check_box)
        return list_check_box

