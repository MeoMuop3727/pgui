import pygame

from dataclasses import dataclass, field
from typing import Optional, Callable, List
from enum import Enum

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import to_array, hex_to_rbg

class StateRadioButton(Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleRadioButton: 
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
