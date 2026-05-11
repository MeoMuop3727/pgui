"""
ScrollView Module
=================
This module provides a scrollable viewport UI component built on top of pygame and numpy.
Content larger than the viewport is rendered through clipping, with a draggable
scrollbar indicating and controlling the current scroll position.

It includes:
- `StateScrollbar`  : Enum defining the visual states of the scrollbar.
- `StyleScrollView` : Dataclass holding all style/configuration options for a scroll view.
- `ScrollView`      : Renders a clipped viewport with mouse wheel and drag scrolling.

Typical usage:
>>> def render_content(surface: pygame.Surface, offset: np.ndarray):
        for i, item in enumerate(items):
            y = 10 + i * 40 - int(offset[1])
            pygame.draw.rect(surface, (200, 200, 200), (10, y, 280, 30))
>>> style = StyleScrollView(
        pos=(50, 50),
        size=(300, 300),
        content_size=(300, 800),
        direction="vertical"
    ) 
    scroll = ScrollView(surface, style, render_func=render_content)
    scroll.update() # Inside game loop
"""

import pygame
import numpy as np

from dataclasses import dataclass, field
from typing import Callable, Optional, Literal
from enum import Enum
from pgui_module.utils.utils_typing import Vec2, ColorType

from pgui_module.utils.utils_transform import hex_to_rbg, to_array

class StateScrollbar(Enum):

    """
    Enum representing the visual states of the scrollbar thumb.

    States
    ------
    NORMAL : int
        Default state — no interaction is occurring.
    HOVER : int
        The mouse cursor is hovering over the scrollbar thumb.
    PRESSED : int
        Reserved for future use — scrollbar is being pressed.
    ACTIVE : int
        The scrollbar thumb is currently being dragged.
    """

    NORMAL = 1
    HOVER = 2
    PRESSED = 3
    ACTIVE = 4
@dataclass(slots=True)
class StyleScrollView:

    """
    Dataclass containing all visual and behavioral configuration for a ScrollView.

    Attributes
    ----------
    pos : Vec2
        Position (x, y) of the viewport on the surface. Defaults to (0, 0).
    size : Vec2
        Size (width, height) of the visible viewport. Defaults to (300, 300).
    content_size : Vec2
        Total size (width, height) of the scrollable content area.
        Should be larger than ``size`` to enable scrolling. Defaults to (300, 800).
    border_radius : int
        Corner radius of the viewport background rect. Defaults to 0.
    scrollbar_border_radius : int
        Corner radius of the scrollbar thumb rect. Defaults to 0.
    direction : Literal["vertical", "horizontal"]
        Scroll direction. Defaults to "vertical".
    scroll_speed : int
        Number of pixels scrolled per mouse wheel tick. Defaults to 30.
    visible : bool
        Whether the scroll view is rendered. Defaults to True.
    bg_color : ColorType
        Background color of the viewport. Defaults to #f0f0f0.

    Scrollbar
    ---------
    show_scrollbar : bool
        Whether the scrollbar thumb is rendered. Defaults to True.
    scrollbar_width : int
        Thickness of the scrollbar thumb in pixels. Defaults to 10.
    scrollbar_color : ColorType
        Scrollbar color in normal state. Defaults to #999999.
    scrollbar_color_hover : ColorType
        Scrollbar color when hovered. Defaults to #777777.
    scrollbar_color_active : ColorType
        Scrollbar color when being dragged. Defaults to #555555.
    scrollbar_color_pressed : ColorType
        Scrollbar color when pressed. Defaults to #555555.
    """

    pos: Vec2 = (0, 0)
    size: Vec2 = (300, 300)

    content_size: Vec2 = (300, 800)

    border_radius: int = 0

    scrollbar_border_radius: int = 0

    direction: Literal["vertical", "horizontal"] = "vertical"

    scroll_speed: int = 30
    visible: bool = True

    bg_color: ColorType = "#f0f0f0"

    # scrollbar
    show_scrollbar: bool = True
    scrollbar_width: int = 10

    scrollbar_color: ColorType = "#999999"
    scrollbar_color_hover: ColorType = "#777777"
    scrollbar_color_active: ColorType = "#555555"
    scrollbar_color_pressed: ColorType = "#555555"
class ScrollView:

    """
    A scrollable viewport component that clips content to a fixed visible area
    and provides mouse wheel scrolling and scrollbar drag interaction.

    Content is rendered via a user-supplied ``render_func`` which receives
    the main surface and the current offset array. The offset represents
    how many pixels the content has been scrolled from its origin.

    The viewport uses ``set_clip`` to restrict drawing to the visible area,
    ensuring content outside the viewport is not rendered.

    Offset
    ------
    ``offset`` is a numpy array ``[offset_x, offset_y]`` representing the
    number of pixels scrolled from the content origin:
    - ``offset[1] = 0``   → content at top (vertical)
    - ``offset[1] = 500`` → content scrolled down 500px

    The render_func must subtract offset from each item's position
    to simulate scrolling:
        y = item_y - offset[1]

    Rendering order (back to front)
    --------------------------------
    1. Background   (viewport background rect)
    2. Content      (clipped to viewport, rendered via render_func)
    3. Scrollbar    (thumb drawn on top, only if show_scrollbar is True)

    Scrollbar position
    ------------------
    - Vertical   : anchored to the right edge of the viewport.
    - Horizontal : anchored to the bottom edge of the viewport.
    Thumb size and position scale proportionally to the offset and content size.

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which the scroll view is drawn.

>>> style : StyleScrollView

        The style/configuration object for this scroll view.

>>> render_func : Callable[[pygame.Surface, np.ndarray], None], optional

        Function called each frame to render scrollable content.
        Receives the main surface and the current offset array.

    Methods
    -------
>>> update() -> None

        Handles mouse wheel and drag input, clamps offset, rebuilds
        the scrollbar, and renders all elements each frame.
        Does nothing if ``StyleScrollView.visible`` is False.

    Example
    -------
>>> def render(surface, offset):
            for i in range(20):
                y = 10 + i * 40 - int(offset[1])
                pygame.draw.rect(surface, (180, 180, 180), (10, y, 280, 30))
>>> style = StyleScrollView(
            pos=(50, 50),
            size=(300, 400),
            content_size=(300, 900),
            scroll_speed=20
        )
        scroll = ScrollView(screen, style, render_func=render)
        # Inside game loop
        scroll.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleScrollView, 
                 render_func: Optional[Callable[[pygame.Surface, np.ndarray], None]] = None):
        self.__surface = surface
        self.__style = style
        self.__render_func = render_func

        self.__offset = np.array([0.0, 0.0])

        self.__viewport_rect = pygame.Rect(self.__style.pos, self.__style.size)
        self.__scrollbar_rect = pygame.Rect(0,0,0,0)

        self.__dragging = False
        self.__hovered = False
        self.__pressed = False

    def update(self):
        if self.__style.visible:
            self.__handle_wheel()
            self.__handle_drag()
            self.__clamp_offset()
            self.__build_scrollbar()

            self.__draw_bg()
            self.__draw_content()
            self.__draw_scrollbar()
            
    def __handle_wheel(self):
        mouse = pygame.mouse.get_pos()
        if not self.__viewport_rect.collidepoint(mouse): return

        for e in pygame.event.get(pygame.MOUSEWHEEL):
            if self.__style.direction == "vertical":
                self.__offset[1] -= e.y * self.__style.scroll_speed
            else:
                self.__offset[0] -= e.y * self.__style.scroll_speed

    def __clamp_offset(self):
        view = to_array(self.__style.size)
        content = to_array(self.__style.content_size)

        max_offset = np.maximum(content - view, 0)
        self.__offset = np.clip(self.__offset, 0, max_offset)

    def __build_scrollbar(self) -> None:
        view = to_array(self.__style.size)
        content = to_array(self.__style.content_size)

        ratio = view / content

        if self.__style.direction == "vertical":
            height = view[1] * ratio[1]
            y = self.__viewport_rect.top + (self.__offset[1] / content[1]) * view[1]

            self.__scrollbar_rect = pygame.Rect(
                self.__viewport_rect.right - self.__style.scrollbar_width,
                int(y),
                self.__style.scrollbar_width,
                int(height)
            )
        else:
            width = view[0] * ratio[0]
            x = self.__viewport_rect.left + (self.__offset[0] / content[0]) * view[0]

            self.__scrollbar_rect = pygame.Rect(
                int(x),
                self.__viewport_rect.bottom - self.__style.scrollbar_width,
                int(width),
                self.__style.scrollbar_width
            )

    def __handle_drag(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        self.__hovered = self.__scrollbar_rect.collidepoint(mouse)

        if pressed and self.__hovered: self.__dragging = True
        if not pressed: self.__dragging = False

        if self.__dragging:
            view = to_array(self.__style.size)
            content = to_array(self.__style.content_size)

            if self.__style.direction == "vertical":
                rel = mouse[1] - self.__viewport_rect.top
                self.__offset[1] = (rel / view[1]) * content[1]
            else:
                rel = mouse[0] - self.__viewport_rect.left
                self.__offset[0] = (rel / view[0]) * content[0]

    def __draw_bg(self):
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), self.__viewport_rect, border_radius=self.__style.border_radius)

    def __draw_content(self):
        old_clip = self.__surface.get_clip()
        self.__surface.set_clip(self.__viewport_rect)

        if self.__render_func:
            self.__render_func(self.__surface, self.__offset)

        self.__surface.set_clip(old_clip)

    def __draw_scrollbar(self):
        if not self.__style.show_scrollbar: return

        visual_state = self.__get_visual_state_scrollbar()
        color = self.__get_color_scrollbar_state(visual_state)

        pygame.draw.rect(self.__surface, color, self.__scrollbar_rect, border_radius=self.__style.scrollbar_border_radius)
    
    def __get_visual_state_scrollbar(self) -> StateScrollbar:
        if self.__hovered: return StateScrollbar.HOVER
        elif self.__dragging: return StateScrollbar.ACTIVE
        elif self.__pressed: return StateScrollbar.PRESSED
        return StateScrollbar.NORMAL
    
    def __get_color_scrollbar_state(self, state: StateScrollbar) -> ColorType:
        if state == StateScrollbar.HOVER: color = self.__style.scrollbar_color_hover
        elif state == StateScrollbar.PRESSED: color = self.__style.scrollbar_color_pressed
        elif state == StateScrollbar.ACTIVE: color = self.__style.scrollbar_color_active
        else: color = self.__style.scrollbar_color

        return hex_to_rbg(color)