import pygame

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from pgui.utils.utils_typing import Vec2, ColorType
from pgui.utils.utils_transform import to_array, hex_to_rbg

@dataclass(slots=True)
class StyleGrid:
    rows: int = 3
    cols: int = 3

    pos: Vec2 = (0, 0)
    area: Vec2 = (500, 500)

    rect: Optional[pygame.Rect] = None

    visible: bool = True

    line_color: ColorType = "#333333"
    line_weight: int = 3

    notes: List[str] = field(default_factory=list)

    font: pygame.font.Font = field(default_factory=lambda: pygame.font.Font(None, 25))
    antialias: bool = True
    color: ColorType = "#333333"

class Grid:
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleGrid):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible

        self.__pos = self.__style.pos if self.__style.rect is None else self.__style.rect.topleft
        self.__area = self.__style.area if self.__style.rect is None else self.__style.rect.size

        self.__line_rows = self.__create_line_row()
        self.__line_cols = self.__create_line_col()
        self.__notes = self.__create_note()

        self.__height_cell = 0
        self.__width_cell = 0
    
    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value

    def update(self) -> None:
        if self.__visible:
            self.__draw_line_row()
            self.__draw_line_col()
            self.__draw_notes()

    def get_size_cel(self) -> Vec2:
        return (self.__width_cell, self.__height_cell)

    def __create_line_row(self) -> List[pygame.Rect]:
        line_rows: List[pygame.Rect] = []

        self.__height_cell = self.__area[0] // self.__style.rows

        for i in range(1, self.__style.rows):
            pos_row = to_array(self.__pos) + to_array((0, self.__height_cell)) * i 
            size_row = to_array((self.__area[0], self.__style.line_weight))

            row = pygame.Rect(
                (int(pos_row[0]), int(pos_row[1])),
                (int(size_row[0]), int(size_row[1]))
            )

            line_rows.append(row)

        return line_rows
    
    def __create_line_col(self) -> List[pygame.Rect]:
        line_cols: List[pygame.Rect] = []

        self.__width_cell = self.__area[0] // self.__style.cols

        for i in range(1, self.__style.cols):
            pos_col = to_array(self.__pos) + to_array((self.__width_cell, 0)) * i 
            size_col = to_array((self.__style.line_weight, self.__area[0]))

            col = pygame.Rect(
                (int(pos_col[0]), int(pos_col[1])),
                (int(size_col[0]), int(size_col[1]))
            )

            line_cols.append(col)

        return line_cols
    
    def __create_note(self) -> List[Tuple[pygame.Surface, Vec2]]:
        notes: List[Tuple[pygame.Surface, Vec2]] = []

        line: int = 0
        count: int = 0

        for _, note in enumerate(self.__style.notes):
            if count >= self.__style.cols:
                line += 1
                count = 0

            pos_note = to_array(self.__pos) + to_array((
                self.__width_cell * count + self.__width_cell // 2, 
                self.__height_cell * line + self.__height_cell // 2
            ))

            text_surface = self.__style.font.render(note, self.__style.antialias, hex_to_rbg(self.__style.color))
            text_rect = text_surface.get_rect(center=(int(pos_note[0]), int(pos_note[1])))

            notes.append((text_surface, text_rect))

            count += 1
        
        return notes

    def __draw_line_row(self) -> None:
        for row in self.__line_rows:
            pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.line_color), row)

    def __draw_line_col(self) -> None:
        for col in self.__line_cols:
            pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.line_color), col)

    def __draw_notes(self) -> None:
        for sur, pos in self.__notes:
            self.__surface.blit(sur, pos)