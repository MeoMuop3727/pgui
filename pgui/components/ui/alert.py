import pygame

from dataclasses import dataclass
from typing import Optional, Literal, Dict

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import to_array, hex_to_rbg
from .button import ButtonText, StyleButton
from .textbox import TextBox, StyleTextBox

@dataclass(slots=True)
class StyleAlert:
    # general
    title: str = ""
    title_color: ColorType = "#222222"

    content: str = ""
    text_color: ColorType = "#222222"
    line_height: int = 0

    type: Literal["error", "warning", "info", "success"] = "info"

    bg_title_color: Optional[ColorType] = None
    bg_content_color: ColorType = "#f0f0f0"

    size: Vec2 = (500, 300)
    pos: Vec2 = (0, 0)

    border: int = 0
    border_color: ColorType = "#000000"

    padding: int = 0

    per_height_title_frame: float = 0.2

    visible: bool = True

    font: pygame.font.Font = pygame.font.Font(None, 25)

    antialias: bool = True

    # normal
    button_color: ColorType = "#333333"
    button_bg_color: ColorType = "#ffb3b3"

    # pressed
    button_color_pressed: ColorType = "#ffffff"
    button_bg_color_pressed: ColorType = "#ff884d"

    # hover
    button_color_hover: ColorType = "#ffffff"
    button_bg_color_hover: ColorType = "#ff884d"

class Alert:
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleAlert):
        self.__surface = surface
        self.__style = style

        self.__pos = style.pos 

        self.__type_color = {
            "error": "#e74c3c",
            "warning": "#f39c12",
            "success": "#27ae60",
            "info": "#3498db"
        }

        self.__content = self.__style.content
        self.__title = self.__style.title

        self.__visible = self.__style.visible

        self.__rect = pygame.Rect(self.__pos, self.__style.size)
        self.__rect_size = self.__rect.size

        self.__size_title_frame = (self.__rect_size[0], self.__rect_size[1] * self.__style.per_height_title_frame)
        self.__size_content_frame = (self.__rect_size[0], self.__rect_size[1] * (1 - self.__style.per_height_title_frame))

        self.__text_box = TextBox(
            self.__surface,
            StyleTextBox(
                content=self.__style.content,
                font=self.__style.font,
                color=self.__style.text_color,
                bg_color=self.__style.bg_content_color,
                antialias=self.__style.antialias,
                pos=(self.__pos[0], self.__pos[1] + self.__size_title_frame[1]),
                size=self.__size_content_frame,
                padding=self.__style.padding,
                line_height=self.__style.line_height
            )
        )

        fix_size_button = (5,5)
        self.__button_close = ButtonText(
            self.__surface,
            StyleButton(
                color=self.__style.button_color,
                color_hover=self.__style.button_color_hover,
                color_pressed=self.__style.button_color_pressed,
                bg_color=self.__style.button_bg_color,
                bg_color_hover=self.__style.button_bg_color_hover,
                bg_color_pressed=self.__style.button_bg_color_pressed,
                content="X",
                on_click=lambda: self.__close_alert(),
                size=to_array((self.__size_title_frame[1], self.__size_title_frame[1])) - 2 * to_array(fix_size_button),
                pos=to_array(self.__pos) + to_array((self.__size_title_frame[0] - self.__size_title_frame[1], 0)) + to_array(fix_size_button)
            )
        )
    
    def update(self):
        if self.__visible:
            self.__draw_border()
            self.__draw_title()
            self.__text_box.update()
            self.__button_close.update()
    
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
    def visible(self, new_visible: bool):
        self.__visible = new_visible
    
    @property
    def title(self) -> str:
        return self.__title
    
    @title.setter
    def title(self, new_title):
        self.__title = new_title
    
    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, new_content):
        self.__content = new_content

    def get_color_type(self) -> Dict[str, str]:
        return self.__type_color
    
    def __draw_title(self):
        title_frame = pygame.Rect(self.__pos, self.__size_title_frame)

        title_surface = self.__style.font.render(self.__style.title, self.__style.antialias, self.__style.title_color)
        title_rect = title_surface.get_rect(center=title_frame.center)

        pygame.draw.rect(self.__surface,
                         hex_to_rbg(self.__style.bg_title_color if self.__style.bg_title_color is not None else self.__type_color[self.__style.type]),
                         title_frame)
        
        self.__surface.blit(title_surface, title_rect)
    
    def __draw_border(self):
        border_width: Vec2 = (self.__style.border, self.__style.border)

        size_border: Vec2 = to_array(self.__style.size) + to_array(border_width) * 2
        pos: Vec2 = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos[0]), int(pos[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border)
    
    def __close_alert(self):
        self.visible = False