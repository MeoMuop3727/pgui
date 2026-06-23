import pygame

from dataclasses import dataclass
from typing import List
from pgui.utils.utils_typing import Vec2, ColorType

from pgui.utils.utils_transform import to_array, hex_to_rbg

@dataclass(slots=True)
class StyleTextBox:
    content: str = ""
    font: pygame.font.Font = pygame.font.Font(None, 25)
    color: ColorType = "#333333"
    bg_color: ColorType = "#cccccc"
    antialias: bool = True
    pos: Vec2 = (0, 0)
    size: Vec2 = (500, 400)
    border: int = 0
    border_radius: int = 0
    border_color: ColorType = "#000000"
    padding: int = 0
    line_height: int = 0
    visible: bool = True

class TextBox: 
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleTextBox):
        self.__surface = surface
        self.__style = style

        self.__visible = style.visible
        self.__pos = style.pos
        self.__content = style.content
        self.__size = style.size 

        self.__rect = pygame.Rect(self.__pos, self.__size)

        self.__list_text = self.__wrap_text()
    
    @property
    def rect(self) -> pygame.Rect:
        return self.__rect
    
    @property
    def size(self) -> str:
        return self.__size
    
    @size.setter
    def size(self, new_size: str):
        self.__size = new_size
    
    @property
    def content(self) -> str:
        return self.__content
    
    @content.setter
    def content(self, new_content: str):
        self.__content = new_content
    
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
            self.__draw_frame()
            self.__draw_content()

    def __draw_frame(self) -> None:
        frame = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), frame, border_radius=self.__style.border_radius)

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        pos_border = to_array(self.__pos) - to_array(border_width)
        size_border = to_array(self.__size) + to_array(border_width) * 2

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)
    
    def __wrap_text(self) -> List[str]:
        list_text: List[str] = []

        current_line = ""
        max_width = self.__size[0] - 2 * self.__style.padding

        for text in self.__content.split(" "):
            text_line = text if current_line == "" else current_line + " " + text

            text_width = self.__style.font.size(text_line)[0]

            if text_width <= max_width:
                current_line = text_line
            else:
                if current_line:
                    list_text.append(current_line)
                current_line = text

        if current_line:
            list_text.append(current_line)

        return list_text

    def __draw_content(self) -> None:
        for line, text_line in enumerate(self.__list_text):
            text_surface = self.__style.font.render(text_line, self.__style.antialias, hex_to_rbg(self.__style.color))
            text_rect = to_array(self.__pos) + to_array((0, text_surface.get_height() * line)) + to_array((self.__style.padding, self.__style.padding))

            self.__surface.blit(text_surface, (int(text_rect[0]), int(text_rect[1])))

