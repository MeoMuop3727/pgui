import pygame

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import hex_to_rbg, to_array

from dataclasses import dataclass

@dataclass
class StylePanel:
    pos: Vec2 = (0, 0)
    size: Vec2 = (500, 500)

    bg_color: ColorType = "#f0f0f0"

    border_color: ColorType = "#000000"
    border_radius: int = 0
    border: int = 0

    padding: int = 0

    visible: bool = True

class Panel:
    def __init__(self,
                 surface: pygame.Surface,
                 style: StylePanel,
                 objects: list = []):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos 

        self.__rect = pygame.Rect(self.__pos, self.__style.size)

        self.__subrect = self.__surface.subsurface(self.__rect)

        self.objects: list = objects
    
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
            self.__draw_border()
            self.__draw_bg()
            self.__draw_objects()
    
    def get_subsurface(self) -> pygame.Surface:
        return self.__subrect

    def __draw_bg(self) -> None:
        bg = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), bg, border_radius=self.__style.border_radius)

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2
        pos_border = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)
    
    def __draw_objects(self) -> None:
        if self.objects:
            for object in self.objects: object(self.__subrect)
