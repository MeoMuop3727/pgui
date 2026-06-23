import pygame

from dataclasses import dataclass
from typing import Optional, Callable, Literal

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import to_array, hex_to_rbg

class StateSwitch:
    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleSwitch:
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
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleSwitch):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos 

        self.__state = self.__style.state

        self.__is_hover = False
        self.__is_pressed = False

        self.__rect = pygame.Rect(self.__pos, self.__style.size)
    
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
            pos_thumb: Vec2 = to_array(self.__pos) + to_array(fix_pos)
        else:
            pos_thumb: Vec2 = to_array(self.__pos) + to_array((int(size_thumb[0]), 0)) + to_array(fix_pos)
        
        thumb = pygame.Rect(
            (int(pos_thumb[0]), int(pos_thumb[1])),
            (int(size_thumb[0]), int(size_thumb[1]))
        )

        pygame.draw.rect(self.__surface, color, thumb, border_radius=100)

    def __draw_border(self, color: ColorType) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        size_border: Vec2 = to_array(self.__style.size) + to_array(border_width) * 2
        pos: Vec2 = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos[0]), int(pos[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, color, border, border_radius=self.__style.border_radius)
    
    