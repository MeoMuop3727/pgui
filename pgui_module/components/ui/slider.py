"""
Slider Module
=============
This module provides a slider UI component built on top of pygame and numpy.
The slider supports both horizontal and vertical orientations, stepped value
snapping, and separates input handling from rendering for flexibility.

It includes:
- `StateSlider`  : Enum defining the visual states of a slider.
- `StyleSlider`  : Dataclass holding all style/configuration options for a slider.
- `Slider`       : Renders an interactive slider with a track, fill, and draggable thumb.

Typical usage:
>>> style = StyleSlider(
        min_value=0,
        max_value=100,
        value=50,
        step=1,
        track_size=(250, 5),
        thumb_size=(20, 20),
        pos=(100, 200)
    )
    slider = Slider(surface, style)
    # Inside game loop
    slider.update()
    # Inside event loop
    slider.input(events)
    # Read current value
    current = slider.value
"""

import pygame
import numpy as np

from dataclasses import dataclass
from typing import Literal, List
from enum import Enum

from pgui_module.utils.utils_typing import Vec2, ColorType, Number
from pgui_module.utils.utils_transform import to_array, hex_to_rbg

class StateSlider(Enum):

    """
    Enum representing the visual states of a Slider thumb.

    States
    ------
    NORMAL : int
        Default state — no interaction is occurring.
    HOVER : int
        The mouse cursor is hovering over the thumb.
    PRESSED : int
        The thumb is currently being dragged by the mouse.
    """

    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleSlider:

    """
    Dataclass containing all visual and layout configuration for a Slider.

    Layout
    ------
    The slider consists of three overlapping elements:
    - Track : the full background bar.
    - Fill  : the colored portion from the track start to the thumb position.
    - Thumb : the draggable indicator that represents the current value.

    Orientation
    -----------
    - ``horizontal`` : thumb moves left to right, fill grows from left.
    - ``vertical``   : thumb moves bottom to top, fill grows from bottom.

    Attributes
    ----------
    min_value : Number
        Minimum value of the slider range. Defaults to 0.
    max_value : Number
        Maximum value of the slider range. Defaults to 100.
    value : Number
        Initial value of the slider. Defaults to 0.
    step : Number
        Snap increment — value is rounded to the nearest multiple of step.
        Defaults to 1.
    orientation : Literal["horizontal", "vertical"]
        Direction of the slider. Defaults to "horizontal".
    track_size : Vec2
        Size (length, thickness) of the track.
        For vertical sliders, axes are swapped internally. Defaults to (250, 5).
    thumb_size : Vec2
        Size (width, height) of the thumb indicator. Defaults to (20, 20).
    pos : Vec2
        Position (x, y) of the track on the surface. Defaults to (0, 0).
    visible : bool
        Whether the slider is rendered. Defaults to True.

    Track
    -----
    track_color : ColorType
        Track background color in normal state.
    track_color_hover : ColorType
        Track color when the thumb is hovered.
    track_color_pressed : ColorType
        Track color when the thumb is being dragged.
    fill_color_active : ColorType
        Color of the filled portion of the track. Defaults to #4caf50.
    track_border_radius : int
        Corner radius of the fill rect. Defaults to 50.

    Thumb
    -----
    thumb_color : ColorType
        Thumb color in normal state. Defaults to #ffffff.
    thumb_color_hover : ColorType
        Thumb color when hovered. Defaults to #f0f0f0.
    thumb_color_pressed : ColorType
        Thumb color when pressed. Defaults to #e0e0e0.
    thumb_border_radius : int
        Corner radius of the thumb rect. Defaults to 50 (circle shape).
    """

    min_value: Number = 0
    max_value: Number = 100
    value: Number = 0
    step: Number = 1

    orientation: Literal["horizontal", "vertical"] = "horizontal"

    track_size: Vec2 = (250, 5)
    thumb_size: Vec2 = (20,20)

    pos: Vec2 = (0, 0)

    visible: bool = True

    # track
    track_color: ColorType = "#cccccc"
    track_color_hover: ColorType = "#bbbbbb"
    track_color_pressed: ColorType = "#bbbbbb"

    fill_color_active: ColorType = "#4caf50"

    track_border_radius: int = 50

    # thumb
    thumb_color: ColorType = "#ffffff"
    thumb_color_hover: ColorType = "#f0f0f0"
    thumb_color_pressed: ColorType = "#e0e0e0"

    thumb_border_radius: int = 50

class Slider:

    """
    An interactive slider component that renders a track, a fill bar,
    and a draggable thumb to represent and control a numeric value.

    Rendering and input are intentionally separated:
    - ``update()`` handles rendering each frame.
    - ``input()``  handles mouse events for dragging.

    Both must be called every frame for the slider to work correctly.

    Rendering order (back to front)
    --------------------------------
    1. Track   (full background bar)
    2. Fill    (colored portion from track start to thumb center)
    3. Thumb   (draggable indicator at the current value position)

    Value calculation
    -----------------
    The thumb position is derived from the current value ratio
    relative to min_value and max_value. When dragging, the mouse
    position is converted back to a value and snapped to the nearest
    step increment.

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which the slider is drawn.

>>> style : StyleSlider

        The style/configuration object for this slider.

    Properties
    ----------
>>> value : Number

        Gets or sets the current value of the slider.
        Setting the value externally does not rebuild rects automatically —
        call ``update()`` to reflect changes visually.

    Methods
    -------
>>> update() -> None

        Determines the visual state and renders the track, fill,
        and thumb each frame.
        Does nothing if ``StyleSlider.visible`` is False.

>>> input(events: List[pygame.event.Event]) -> None

        Processes mouse events to handle thumb dragging.
        Updates value, thumb position, and fill rect when dragging.
        Must be called inside the event loop each frame.

    Example
    -------
>>> style = StyleSlider(
            min_value=0,
            max_value=100,
            value=30,
            step=5,
            track_size=(300, 6),
            pos=(50, 150)
        )

>>> slider = Slider(surface, style)
>>> # Inside game loop
>>> slider.update()
>>> slider.input(pygame.event.get())
>>> volume = slider.value  # → 30
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleSlider):
        self.__surface = surface
        self.__style = style

        self.__is_hovered: bool = False
        self.__is_pressed: bool = False

        self.__value = self.__style.value

        self.__track = self.__build_track_rect()
        self.__thumb = self.__build_thumb_rect()
        self.__fill = self.__build_fill_rect()
    
    def update(self) -> None:
        if self.__style.visible:
            visual_state = self.__get_visual_state()

            track_color = self.__get_track_color_state(visual_state)

            thumb_color = self.__get_thumb_color_state(visual_state)

            self.__draw_track(track_color)
            self.__draw_fill()
            self.__draw_thumb(thumb_color)
    
    def input(self, events: List[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.__is_hovered = self.__thumb.collidepoint(mouse_pos)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.__is_hovered: self.__is_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.__is_pressed = False
        
            if self.__is_pressed: 
                new_value = self.__calc_value_from_pos(mouse_pos)
                if new_value != self.__value: 
                    self.__value = new_value    

                    self.__thumb = self.__build_thumb_rect()
                    self.__fill = self.__build_fill_rect()

    @property
    def value(self) -> Number:
        return self.__value

    @value.setter
    def value(self, value: Number) -> None:
        self.__value = value
    
    def __get_thumb_color_state(self, state: StateSlider) -> ColorType:
        if state == StateSlider.PRESSED: color = self.__style.thumb_color_pressed
        if state == StateSlider.HOVER: color = self.__style.thumb_color_hover
        else: color = self.__style.thumb_color

        return hex_to_rbg(color)
    
    def __get_track_color_state(self, state: StateSlider) -> ColorType:
        if state == StateSlider.PRESSED: color = self.__style.track_color_pressed
        if state == StateSlider.HOVER: color = self.__style.track_color_hover
        else: color = self.__style.track_color

        return hex_to_rbg(color)
    
    def __build_track_rect(self) -> pygame.Rect:
        size = to_array(self.__style.track_size)

        if self.__style.orientation == "horizontal":
            track_size = to_array((size[0], size[1]))
        else:
            track_size = to_array((size[1], size[0]))

        return pygame.Rect(self.__style.pos, (int(track_size[0]), int(track_size[1])))
    
    def __build_thumb_rect(self) -> pygame.Rect:
        center = self.__calc_thumb_pos()
        size = self.__style.thumb_size

        pos = center - np.array((size[0] / 2, size[1] / 2))

        return pygame.Rect((int(pos[0]), int(pos[1])), size)

    def __build_fill_rect(self) -> pygame.Rect:
        track = self.__track

        if self.__style.orientation == "horizontal":
            width = self.__thumb.centerx - track.left
            return pygame.Rect(track.left, track.top, width, track.height)
        else:
            height = track.bottom - self.__thumb.centery
            return pygame.Rect(track.left, self.__thumb.centery, track.width, height)

    def __draw_track(self, color: ColorType) -> None:
        pygame.draw.rect(self.__surface, color, self.__track, border_radius=self.__style.thumb_border_radius)

    def __draw_thumb(self, color: ColorType) -> None:
        pygame.draw.rect(self.__surface, color, self.__thumb, border_radius=self.__style.thumb_border_radius)
    
    def __draw_fill(self) -> None:
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.fill_color_active), self.__fill, border_radius=self.__style.track_border_radius)

    def __get_visual_state(self) -> StateSlider:
        if self.__is_pressed: return StateSlider.PRESSED
        if self.__is_hovered: return StateSlider.HOVER
        return StateSlider.NORMAL
    
    def __calc_thumb_pos(self) -> np.ndarray:
        ratio = (self.__value - self.__style.min_value) / (self.__style.max_value - self.__style.min_value)

        track = self.__track

        if self.__style.orientation == "horizontal":
            x = track.left + ratio * track.width
            y = track.centery
            return np.array((x, y))

        else:
            y = track.bottom - ratio * track.height
            x = track.centerx
            return np.array((x, y))
    
    def __calc_value_from_pos(self, mouse_pos: Vec2) -> float:
        track = self.__track

        if self.__style.orientation == "horizontal":
            ratio = (mouse_pos[0] - track.left) / track.width
        else:
            ratio = (track.bottom - mouse_pos[1]) / track.height

        ratio = max(0, min(1, ratio))

        value = self.__style.min_value + ratio * (self.__style.max_value - self.__style.min_value)

        # step
        step = self.__style.step
        value = round(value / step) * step

        return value
