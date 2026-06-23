import pygame

from dataclasses import dataclass
from pgui.utils.utils_typing import Vec2, ColorType

from pgui.utils.utils_transform import to_array, hex_to_rbg

@dataclass(slots=True)
class StyleLabel:
    content: str = ""
    font: pygame.font.Font = pygame.font.Font(None, 25)
    color: ColorType = "#333333"
    bg_color: ColorType = "#cccccc"
    antialias: bool = True
    pos: Vec2 = (0, 0)
    size: Vec2 = (200, 50)
    border: int = 0
    border_radius: int = 0
    border_color: ColorType = "#000000"
    visible: bool = True

class Label:    
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleLabel):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos 

        self.__rect = pygame.Rect(self.__pos, self.__style.size)

        self.__text = self.__style.content
    
    @property
    def pos(self) -> Vec2:
        return self.__pos

    @pos.setter
    def pos(self, new_pos: Vec2):
        self.__pos = new_pos
        self.__rect = pygame.Rect(self.__pos, self.__style.size)

    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value
        
    def update(self) -> None:
        if self.__visible:
            self.__draw_border()
            self.__draw_frame()
            self.__draw_content()
    
    @property
    def content(self) -> str:
        return self.__text
    
    @content.setter
    def content(self, content: str) -> None:
        self.__text = content

    def __draw_frame(self) -> None:
        frame = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), frame, border_radius=self.__style.border_radius)

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        pos_border = to_array(self.__pos) - to_array(border_width)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)

    def __draw_content(self) -> None:
        text_surface = self.__style.font.render(self.__text, self.__style.antialias, hex_to_rbg(self.__style.color))
        text_rect = text_surface.get_rect(center=self.__rect.center)
        self.__surface.blit(text_surface, text_rect)

