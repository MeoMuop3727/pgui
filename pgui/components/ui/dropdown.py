import pygame

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import to_array, hex_to_rbg

from .button import StyleButton, ButtonText

class StateDropdown(Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3
    OPEN = 4

@dataclass(slots=True)
class StyleDropdown:
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

