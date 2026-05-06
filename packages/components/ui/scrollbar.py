

import pygame
import numpy as np

from dataclasses import dataclass
from typing import Callable, Literal, Optional
from enum import Enum

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg

class StateScrollbar(Enum):
    NORMAL = 1
    HOVER = 2
    ACTIVE = 3
    PRESSED = 4

@dataclass(slots=True)
class StyleScrollView:
    # general
    pos: Vec2 = (0, 0)
    size: Vec2 = (400, 300)

    content_size: Vec2 = (400, 600)

    direction: Literal["vertical", "horizontal", "both"] = "vertical"

    scroll_speed: int = 20
    visible: bool = True

    # background
    bg_color: ColorType = "#f0f0f0"
    border_radius: int = 0

    # scrollbar
    show_scrollbar: bool = True
    scrollbar_size: Vec2 = (8, 10)
    scroll_border_radius: int = 0

    scrollbar_color: ColorType = "#999999"
    scrollbar_color_hover: ColorType = "#777777"
    scrollbar_color_active: ColorType = "#555555"
    scrollbar_color_pressed: ColorType = "#555555"

class ScrollView:
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleScrollView):
        pass
