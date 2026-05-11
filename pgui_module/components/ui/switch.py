"""
Switch Module
=============
This module provides a toggle switch UI component built on top of pygame.

The switch supports two states (ON/OFF) and responds to mouse interaction
with hover, pressed, and active visual feedback. Colors for the track,
thumb, and border are all configurable per state.

It includes:
- `StateSwitch`  : Class defining constants for the visual states of a switch.
- `StyleSwitch`  : Dataclass holding all style/configuration options for a switch.
- `Switch`       : Renders a toggle switch and manages its ON/OFF state.

Typical usage:
>>> style = StyleSwitch(
        track_color="#cccccc",
        track_color_active="#4caf50",
        size=(70, 36),
        on_click=lambda is_on: print(f"Switch is {'ON' if is_on else 'OFF'}")
    )
    switch = Switch(surface, style)
    # Inside game loop
    switch.update()
    # Read current state
    is_on = switch.get_state()
"""

import pygame

from dataclasses import dataclass
from typing import Optional, Callable, Literal

from pgui_module.utils.utils_typing import Vec2, ColorType
from pgui_module.utils.utils_transform import to_array, hex_to_rbg

class StateSwitch:

    """
    Constants representing the visual states of a Switch.

    States
    ------
    NORMAL : int
        Default state — no interaction is occurring.
    HOVER : int
        The mouse cursor is hovering over the switch.
    PRESSED : int
        The switch is currently being held down by the mouse.

    Note
    ----
    The active (ON/OFF) state of the switch is tracked separately
    via `Switch.__state` and overlays the visual state when ON.
    """

    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleSwitch:

    """
    Dataclass containing all visual and behavioral configuration for a Switch.

    State-based styling
    -------------------
    Each visual property (track_color, thumb_color, border_color) has four
    variants corresponding to the interaction state: normal, hover, pressed,
    and active (ON). The active state takes priority over all other states
    when the switch is toggled ON.

    Attributes
    ----------
    track_color : ColorType
        Track background color in normal state.
    thumb_color : ColorType
        Thumb color in normal state.
    border_color : ColorType
        Border color in normal state.

    track_color_pressed : ColorType
        Track color when pressed.
    thumb_color_pressed : ColorType
        Thumb color when pressed.
    border_color_pressed : ColorType
        Border color when pressed.

    track_color_hover : ColorType
        Track color when hovered.
    thumb_color_hover : ColorType
        Thumb color when hovered.
    border_color_hover : ColorType
        Border color when hovered.

    track_color_active : ColorType
        Track color when the switch is ON.
    thumb_color_active : ColorType
        Thumb color when the switch is ON.
    border_color_active : ColorType
        Border color when the switch is ON.

    General
    -------
    border : int
        Border thickness in pixels. 0 means no border.
    border_radius : int
        Corner radius for the track and border. Defaults to 50 (pill shape).
    on_click : Callable[[bool], None], optional
        Callback triggered when the switch is toggled.
        Receives the new state as a boolean.
    on_sound : pygame.mixer.Sound, optional
        Sound played when the switch is toggled.
    size : Vec2
        Size (width, height) of the switch track.
    pos : Vec2
        Position (x, y) of the switch on the surface.
    state : bool or Literal[0, 1]
        Initial ON/OFF state of the switch. Defaults to 0 (OFF).
    visible : bool
        Whether the switch is rendered and interactive. Defaults to True.
    padding : int
        Inner spacing between the track edge and the thumb.
    """

    # normal
    track_color: ColorType = "#cccccc"
    thumb_color: ColorType = "#333333"
    border_color: ColorType = "#000000"

    # pressed
    track_color_pressed: ColorType = "#333333"
    thumb_color_pressed: ColorType = "#cccccc"
    border_color_pressed: ColorType = "#000000"

    # hover
    track_color_hover: ColorType = "#333333"
    thumb_color_hover: ColorType = "#cccccc"
    border_color_hover: ColorType = "#000000"

    # active
    track_color_active: ColorType = "#333333"
    thumb_color_active: ColorType = "#cccccc"
    border_color_active: ColorType = "#000000"

    # general
    border: int = 0
    border_radius: int = 50

    on_click: Optional[Callable[[bool], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

    size: Vec2 = (70, 36)
    pos: Vec2 = (0, 0)

    state: Literal[0, 1] | bool = 0

    visible: bool = True

    padding: int = 5

class Switch:

    """
    A toggle switch component that renders a track and a sliding thumb,
    and manages an ON/OFF state triggered by mouse clicks.

    When clicked, the switch toggles its internal state and moves
    the thumb from left (OFF) to right (ON). Colors for all visual
    elements update based on the current interaction and toggle state.

    Rendering order (back to front)
    --------------------------------
    1. Border  (slightly larger rect behind the track)
    2. Track   (the background pill shape)
    3. Thumb   (the sliding indicator inside the track)

    State priority
    --------------
    Active (ON) state overrides hover and pressed colors,
    ensuring the ON appearance is always visually distinct.

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which the switch is drawn.

>>> style : StyleSwitch

        The style/configuration object for this switch.

    Methods
    -------
>>> update() -> None

        Handles mouse interaction, updates toggle state,
        and draws the switch each frame.
        Does nothing if `StyleSwitch.visible` is False.

>>> get_state() -> bool or Literal[0, 1]

        Returns the current ON/OFF state of the switch.

    Example
    -------
>>> style = StyleSwitch(
            track_color_active="#4caf50",
            size=(70, 36),
            on_click=lambda is_on: print(is_on)
        )
        switch = Switch(surface, style)
        # Inside game loop
        switch.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleSwitch):

        self.__surface = surface
        self.__style = style

        self.__state = self.__style.state

        self.__is_hover = False
        self.__is_pressed = False

        self.__rect = pygame.Rect(self.__style.pos, self.__style.size)
    
    def update(self) -> None:
        if self.__style.visible:
            mouse_pos = pygame.mouse.get_pos()
            self.__is_hover = self.__rect.collidepoint(mouse_pos)
            
            if self.__is_hover and pygame.mouse.get_pressed()[0]:
                if not self.__is_pressed: 
                    self.__is_pressed = True
                    self.__state = not self.__state
            else:
                if self.__is_pressed and self.__is_hover:
                    if self.__style.on_click is not None and self.__state: self.__style.on_click()
                    if self.__style.on_sound is not None: self.__style.on_sound.play()
                self.__is_pressed = False
                        
            visual_state = self.__get_visual_state()

            color_track = self.__get_track_color_state(visual_state)
            color_thumb = self.__get_thumb_color_state(visual_state)
            color_border = self.__get_border_color_state(visual_state)

            self.__draw_border(color_border)
            self.__draw_track(color_track)
            self.__draw_thumb(color_thumb)

    def get_state(self) -> Literal[0,1] | bool:
        return self.__state

    def __get_visual_state(self) -> StateSwitch:
        if self.__is_hover: return StateSwitch.HOVER
        elif self.__is_pressed: return StateSwitch.PRESSED
        return StateSwitch.NORMAL

    def __get_track_color_state(self, state: StateSwitch) -> ColorType:
        if state == StateSwitch.PRESSED: color = self.__style.track_color_pressed
        elif state == StateSwitch.HOVER: color = self.__style.track_color_hover
        else: color = self.__style.track_color

        if self.__state: color = self.__style.track_color_active

        return hex_to_rbg(color)
    
    def __get_thumb_color_state(self, state: StateSwitch) -> ColorType:
        if state == StateSwitch.PRESSED: color = self.__style.thumb_color_pressed
        elif state == StateSwitch.HOVER: color = self.__style.thumb_color_hover
        else: color = self.__style.thumb_color

        if self.__state: color = self.__style.thumb_color_active

        return hex_to_rbg(color)
    
    def __get_border_color_state(self, state: StateSwitch) -> ColorType:
        if state == StateSwitch.PRESSED: color = self.__style.border_color_pressed
        elif state == StateSwitch.HOVER: color = self.__style.border_color_hover
        else: color = self.__style.border_color

        if self.__state: color = self.__style.border_color_active

        return hex_to_rbg(color)

    def __draw_track(self, color: ColorType) -> None:
        track = self.__rect
        pygame.draw.rect(self.__surface, color, track, border_radius=self.__style.border_radius)

    def __draw_thumb(self, color: ColorType) -> None:
        padding: Vec2 = (self.__style.padding, self.__style.padding)

        size_thumb: Vec2 = to_array((self.__style.size[0] // 2, self.__style.size[1])) - to_array(padding)

        fix_pos = (5,2)

        if not self.__state:
            pos_thumb: Vec2 = to_array(self.__style.pos) + to_array(fix_pos)
        else:
            pos_thumb: Vec2 = to_array(self.__style.pos) + to_array((int(size_thumb[0]), 0)) + to_array(fix_pos)
        
        thumb = pygame.Rect(
            (int(pos_thumb[0]), int(pos_thumb[1])),
            (int(size_thumb[0]), int(size_thumb[1]))
        )

        pygame.draw.rect(self.__surface, color, thumb, border_radius=100)

    def __draw_border(self, color: ColorType) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        size_border: Vec2 = to_array(self.__style.size) + to_array(border_width) * 2
        pos: Vec2 = to_array(self.__style.pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos[0]), int(pos[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, color, border, border_radius=self.__style.border_radius)
    
    