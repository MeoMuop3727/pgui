import pygame
import numpy as np

from dataclasses import dataclass
from typing import Literal, List
from enum import Enum

from pgui.utils.utils_typing import Vec2, ColorType, Number
from pgui.utils.utils_transform import to_array, hex_to_rbg

class StateSlider(Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleSlider:
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
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleSlider):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos 

        self.__is_hovered: bool = False
        self.__is_pressed: bool = False

        self.__value = self.__style.value

        self.__track = self.__build_track_rect()
        self.__thumb = self.__build_thumb_rect()
        self.__fill = self.__build_fill_rect()
    
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

        return pygame.Rect(self.__pos, (int(track_size[0]), int(track_size[1])))
    
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
