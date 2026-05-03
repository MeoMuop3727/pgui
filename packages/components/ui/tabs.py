"""
Tab Module
==========
This module provides a tab-based UI component built on top of pygame,
using `ButtonText` internally to render clickable tab panels.

It includes:
- `StyleTab`  : Dataclass holding all style/configuration options for a tab.
- `TabPanel`  : Renders a row/column of clickable tab buttons and tracks the active tab.
- `TabFrame`  : Renders the content area corresponding to the active tab.
- `Tab`       : Top-level component combining `TabPanel` and `TabFrame` into one widget.

Typical usage:
    def render_home(surface): ...
    def render_settings(surface): ...

    style = StyleTab(
        tabs_list=["Home", "Settings"],
        tabs_func=[render_home, render_settings],
        tab_panel_type="horizontal",
        size=(700, 500)
    )
    tab = Tab(surface, style)

    # Inside game loop
    tab.update()
"""

import pygame

from dataclasses import dataclass, field
from typing import Callable, Optional, Literal, List
from packages.utils.utils_typing import Vec2, ColorType

from packages.utils.utils_transform import hex_to_rbg, to_array
from .button import ButtonText, StyleButton

@dataclass(slots=True)
class StyleTab:

    """
    Dataclass containing all visual and behavioral configuration for a Tab component.

    Tab Panel Styling
    -----------------
    Each tab button supports four visual states: normal, hover, pressed, and active.
    The active state represents the currently selected tab.

    Attributes
    ----------
    tabs_list : List[str]
        Labels for each tab button.
    tabs_func : List[Callable, optional]
        Callback functions for each tab's content area.
        Each function receives either a subsurface or no argument:
            - func(surface: pygame.Surface) → renders into the frame
            - func()                        → renders independently

    color : ColorType
        Text color in normal state.
    bg_color : ColorType
        Background color in normal state.

    color_hover : ColorType
        Text color when hovered.
    bg_color_hover : ColorType
        Background color when hovered.

    color_pressed : ColorType
        Text color when pressed.
    bg_color_pressed : ColorType
        Background color when pressed.

    color_active : ColorType
        Text color of the currently active tab.
    bg_color_active : ColorType
        Background color of the currently active tab.

    General
    -------
    font : pygame.font.Font
        Font used to render tab labels.
    pos : Vec2
        Position (x, y) of the entire tab component on the surface.
    percent_width_tab_panel : float
        Fraction of total width allocated to the tab panel (horizontal layout).
    percent_height_tab_panel : float
        Fraction of total height allocated to the tab panel (vertical layout).
    size : Vec2
        Total size (width, height) of the tab component.
    active_tab : int
        Index of the initially active tab. Defaults to 0.
    visible : bool
        Whether the tab component is rendered. Defaults to True.
    tab_panel_type : Literal["horizontal", "vertical"]
        Layout direction of the tab panel.
        - "horizontal" : tab buttons are stacked vertically on the left side.
        - "vertical"   : tab buttons are arranged horizontally along the top.
    bg_frame_color : ColorType
        Background color of the content frame area.
    """

    # tab panel
    tabs_list: List[str] = field(default_factory=lambda: ["Tab 1"])
    tabs_func: List[Optional[Callable[[], None]]] = field(default_factory=lambda: [])

    # normal tab panel
    color: ColorType = "#ffffff"
    bg_color: ColorType = "#f0f0f0"

    # hover tab panel
    color_hover: ColorType = "#333333"
    bg_color_hover: ColorType = "#f1f0f2"

    # pressed tab panel
    color_pressed: ColorType = "#333333"
    bg_color_pressed: ColorType = "#f1f0f2"

    # active tab panel
    color_active: ColorType = "#888888"
    bg_color_active: ColorType = "#cccccc"

    # general
    font: pygame.font.Font = pygame.font.Font(None, 25)
    pos: Vec2 = (0,0)
    percent_width_tab_panel: float = 0.35
    percent_height_tab_panel: float = 0.25
    size: Vec2 = (700, 500)
    active_tab: int = 0
    visible: bool = True
    tab_panel_type: Literal["horizontal", "vertical"] = "horizontal"
    bg_frame_color: ColorType = "#cccccc"

class TabPanel:

    """
    Renders a list of clickable tab buttons and tracks the currently active tab.

    Tab buttons are created from `StyleTab.tabs_list` and laid out according
    to `StyleTab.tab_panel_type`. Clicking a tab updates the active index
    and rebuilds the button list to reflect the new active style.

    Attributes
    ----------
    surface : pygame.Surface
        The surface on which tab buttons are drawn.
    style : StyleTab
        The style/configuration object for this tab panel.

    Methods
    -------
    update() -> None
        Draws and updates all tab buttons each frame.
    get_size_tab_panel() -> Vec2
        Returns the size (width, height) of a single tab button.
    get_tab_panel_active() -> int
        Returns the index of the currently active tab.
    """

    def __init__(self, 
                 surface: pygame.Surface,
                 style: StyleTab):
        self.__surface = surface
        self.__style = style

        self.__active_tab = self.__style.active_tab
    
        self.__list_panel = self.__create_list_tabs_panel()

    def update(self) -> None:
        self.__draw_tabs_panel()

    def get_size_tab_panel(self) -> Vec2:
        return self.__list_panel[0].size_button

    def get_tab_panel_active(self) -> int:
        return self.__active_tab

    def __draw_tabs_panel(self) -> None:
        if self.__list_panel:
            for tab_panel in self.__list_panel:
                tab_panel.update()

    def __create_list_tabs_panel(self) -> List[ButtonText]:
        list_panel: List[ButtonText] = []

        if self.__style.tab_panel_type == "horizontal":
            width_tab_panel = self.__style.size[0] * self.__style.percent_width_tab_panel
            height_tab_panel = self.__style.size[1] // len(self.__style.tabs_list)
        
        if self.__style.tab_panel_type == "vertical":
            width_tab_panel = self.__style.size[0] // len(self.__style.tabs_list)
            height_tab_panel = self.__style.size[1] * self.__style.percent_height_tab_panel

        for index, panel in enumerate(self.__style.tabs_list):
            if self.__style.tab_panel_type == "horizontal":
                pos_tab_panel = to_array(self.__style.pos) + to_array((0, height_tab_panel)) * index
            
            if self.__style.tab_panel_type == "vertical":
                pos_tab_panel = to_array(self.__style.pos) + to_array((width_tab_panel, 0)) * index

            button = ButtonText(
                surface=self.__surface,
                style=StyleButton(
                    color=self.__style.color if index != self.__active_tab else self.__style.color_active,
                    color_hover=self.__style.color_hover,
                    color_pressed=self.__style.color_pressed,
                    bg_color=self.__style.bg_color if index != self.__active_tab else self.__style.bg_color_active,
                    bg_color_hover=self.__style.bg_color_hover,
                    bg_color_pressed=self.__style.bg_color_pressed,
                    font=self.__style.font,
                    size=(width_tab_panel, height_tab_panel),
                    pos=pos_tab_panel,
                    content=panel,
                    on_click=lambda i = index: self.__on_click(i)
                )
            )

            list_panel.append(button)

        return list_panel
    
    def __on_click(self, index_active: int) -> None:
        if index_active < 0 or index_active >= len(self.__style.tabs_list): return

        if index_active == self.__active_tab: return

        self.__active_tab = index_active
        self.__list_panel = self.__create_list_tabs_panel()

class TabFrame:

    """
    Renders the content area corresponding to the currently active tab.

    The frame is positioned adjacent to the `TabPanel` — to the right
    for horizontal layouts, or below for vertical layouts. On each
    `update()` call, it fills the frame background and invokes the
    active tab's render function.

    The render function in `StyleTab.tabs_func` is called with a subsurface
    if it accepts a surface argument, otherwise it is called with no arguments.

    Attributes
    ----------
    surface : pygame.Surface
        The surface on which the frame is drawn.
    style : StyleTab
        The style/configuration object for this tab frame.

    Methods
    -------
    update(active_tab: int) -> None
        Redraws the frame background and invokes the active tab's render function.
    get_pos_surface_frame_content() -> Vec2
        Returns the top-left position of the content frame on the surface.
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleTab):
        self.__surface = surface
        self.__style = style

        self.__tab_panel = TabPanel(surface, style)

        self.__frame_content = self.__create_frame_content()

        self.__pos_tab_frame = ...
    
    def update(self, active_tab: int) -> None:
        subframe = self.__surface.subsurface(self.__frame_content)

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_frame_color), self.__frame_content)

        self.__active_tab_frame(subframe, active_tab)
    
    def get_pos_surface_frame_content(self) -> Vec2:
        return self.__pos_tab_frame

    def __create_frame_content(self) -> pygame.Rect:
        size_tab_panel = self.__tab_panel.get_size_tab_panel()

        if self.__style.tab_panel_type == "horizontal":
            width_tab_frame = self.__style.size[0] - size_tab_panel[0]
            height_tab_frame = self.__style.size[1]

            self.__pos_tab_frame = to_array(self.__style.pos) + to_array((size_tab_panel[0], 0))

        if self.__style.tab_panel_type == "vertical":
            width_tab_frame = self.__style.size[0]
            height_tab_frame = self.__style.size[1] - size_tab_panel[1]

            self.__pos_tab_frame = to_array(self.__style.pos) + to_array((0, size_tab_panel[1]))
        
        frame_content = pygame.Rect(
            (int(self.__pos_tab_frame[0]), int(self.__pos_tab_frame[1])),
            (width_tab_frame, height_tab_frame)
        )

        return frame_content
    
    def __active_tab_frame(self, surface: Optional[pygame.Surface], active_tab: int) -> None:
        if active_tab >= 0 and active_tab < len(self.__style.tabs_func):
            if self.__style.tabs_func[active_tab]:
                try:
                    self.__style.tabs_func[active_tab](surface)
                except Exception:
                    self.__style.tabs_func[active_tab]()

class Tab:

    """
    Top-level tab component combining `TabPanel` and `TabFrame` into one widget.

    Manages the full tab UI: renders the clickable tab buttons via `TabPanel`
    and the corresponding content area via `TabFrame`, keeping both in sync
    through the active tab index.

    Attributes
    ----------
    style : StyleTab
        The style/configuration object controlling layout and appearance.

    Methods
    -------
    update() -> None
        Updates and renders both the tab panel and the content frame each frame.
        Does nothing if `StyleTab.visible` is False.

    Example
    -------
        style = StyleTab(
            tabs_list=["Home", "Settings"],
            tabs_func=[render_home, render_settings],
            size=(700, 500)
        )
        tab = Tab(surface, style)

        # Inside game loop
        tab.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleTab):
        self.__style = style

        self.__tab_panel = TabPanel(surface, style)
        self.__tab_frame = TabFrame(surface, style)
    
    def update(self) -> None:
        if self.__style.visible:
            self.__tab_panel.update()
            self.__tab_frame.update(self.__tab_panel.get_tab_panel_active())

