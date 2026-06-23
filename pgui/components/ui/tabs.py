import pygame

from dataclasses import dataclass, field
from typing import Callable, Optional, Literal, List
from pgui.utils.utils_typing import Vec2, ColorType

from pgui.utils.utils_transform import hex_to_rbg, to_array
from pgui.components.ui.button import ButtonText, StyleButton

@dataclass(slots=True)
class StyleTab:
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
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleTab):
        self.__visible = style.visible

        self.__tab_panel = TabPanel(surface, style)
        self.__tab_frame = TabFrame(surface, style)
    
    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value
    
    def update(self) -> None:
        if self.__visible:
            self.__tab_panel.update()
            self.__tab_frame.update(self.__tab_panel.get_tab_panel_active())

