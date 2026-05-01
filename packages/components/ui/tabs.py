


import pygame

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Literal, List
from packages.utils.utils_typing import Vec2, ColorType, PaddingType

from packages.utils.utils_transform import hex_to_rbg, to_array

@dataclass
class StyleTab:
    # tab panel
    tabs_list: Dict[str, Callable[[], None]] = {"Tab 1": None}

    # normal tab panel
    color: ColorType = "#ffffff"
    bg_color: ColorType = "#f0f0f0"

    # hover tab panel
    color_hover: ColorType = "#333333"
    bg_color_hover: ColorType = "#f1f0f2"

    # pressed tab panel
    color_pressed: ColorType = "#333333"
    bg_color_pressed: ColorType = "#f1f0f2"

     # disable
    color_disable: ColorType = "#888888"
    bg_color_disable: ColorType = "#cccccc"

    # general
    font: pygame.font.Font = pygame.font.Font(None, 25)
    pos: Vec2 = (0,0)
    percent_width_tab_panel: float = 0.35
    size: Vec2 = (700, 500)
    border: int = 1
    border_radius: int = 0
    border_color: ColorType = "#000000"
    active_tab: int = 0
    title: str = ""
    title_color: ColorType = "#f0f0f0"
    visible: bool = True
    padding: PaddingType = (0, 0, 0, 0)
    unactive_tabs: List[int] = []

class TabPanel:
    def __init__(self):
        pass

class TabFrame:
    def __init__(self):
        pass

class Tab:
    def __init__(self):
        pass
