"""
Grid Module
===========
This module provides a grid UI component built on top of pygame.

The grid renders a configurable row/column layout
with divider lines and optional text notes
centered inside each cell.

It includes:
- `StyleGrid` : Dataclass holding all visual
                and layout configuration for a grid.
- `Grid`      : Renders divider lines
                and optional notes inside grid cells.

Typical usage:
    >>> style = StyleGrid(
        rows=3,
        cols=3,
        area=(500, 500),
        pos=(50, 50),
        notes=[
            "A1", "A2", "A3",
            "B1", "B2", "B3"
        ]
    )
    grid = Grid(surface, style)
    # Inside game loop
    grid.update()
    # Or use rect directly
    style = StyleGrid(
        rows=4,
        cols=4,
        rect=pygame.Rect(50, 50, 400, 400)
    )
"""

import pygame

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg

@dataclass(slots=True)
class StyleGrid:

    """
    Dataclass containing all visual and layout configuration for a Grid.

    Position
    --------
    The grid position and size can be specified in two ways:

    - ``pos`` + ``area`` :
        Explicit top-left position and total grid size.

    - ``rect`` :
        A pygame.Rect that overrides both ``pos`` and ``area``.

    Grid layout
    -----------
    The grid is divided into equal-sized cells based on ``rows`` and ``cols``.

    Divider lines are automatically generated between cells.

    Optional notes can be rendered centered inside each cell, filled left-to-right and top-to-bottom.

    Attributes
    ----------
    >>> rows : int

        Number of rows in the grid. Defaults to 3.

    >>> cols : int

        Number of columns in the grid. Defaults to 3.

    >>> pos : Vec2

        Position (x, y) of the grid top-left corner.

    >>> area : Vec2

        Total size (width, height) of the grid.

    >>> rect : pygame.Rect, optional

        Overrides both ``pos`` and ``area`` when provided.

    >>> visible : bool

        Whether the grid is rendered. Defaults to True.

    >>> line_color : ColorType

        Color of divider lines.

    >>> line_weight : int

        Thickness of divider lines in pixels.

    >>> notes : List[str]

        Text labels rendered centered inside each cell.
        Notes are filled left-to-right, top-to-bottom.
        Remaining cells stay empty if fewer notes are provided.

    >>> font : pygame.font.Font

        Font used to render notes.

    >>> antialias : bool

        Whether note text rendering uses antialiasing.

    >>> color : ColorType

        Text color of notes.
    """

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

    """
    A grid component that renders
    horizontal and vertical divider lines
    with optional centered notes inside cells.

    The grid is divided into equal-sized cells
    based on ``rows`` and ``cols``.

    Divider lines separate rows and columns,
    while notes are rendered centered
    inside each cell.

    Notes are distributed
    left-to-right
    and top-to-bottom.

    Position resolution
    -------------------
    If ``StyleGrid.rect`` is provided,
    it overrides both
    ``StyleGrid.pos`` and ``StyleGrid.area``.

    Rendering order (back to front)
    --------------------------------
    1. Row dividers
    (horizontal lines between rows)

    2. Column dividers
    (vertical lines between columns)

    3. Notes
    (text centered inside cells)

    Cell size calculation
    ---------------------
    >>> width_cell  = area[0] // cols

    >>> height_cell = area[0] // rows

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which the grid is drawn.

    >>> style : StyleGrid

        The style/configuration object for this grid.

    Methods
    -------
    >>> update() -> None

        Draws divider lines and notes each frame.
        Does nothing if ``StyleGrid.visible`` is False.

    >>> get_size_cel() -> Vec2

        Returns the size of a single cell.
        Format: ``(width, height)``

    Example
    -------
>>> style = StyleGrid(
            rows=4,
            cols=4,
            area=(400, 400),
            pos=(100, 100),
            line_color="#aaaaaa",
            notes=[
                "Mon", "Tue",
                "Wed", "Thu"
            ]
        )
        grid = Grid(surface, style)
        # Inside game loop
        grid.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleGrid):
        self.__surface = surface
        self.__style = style

        self.__pos = self.__style.pos if self.__style.rect is None else self.__style.rect.topleft
        self.__area = self.__style.area if self.__style.rect is None else self.__style.rect.size

        self.__line_rows = self.__create_line_row()
        self.__line_cols = self.__create_line_col()
        self.__notes = self.__create_note()

        self.__height_cell = 0
        self.__width_cell = 0

    def update(self) -> None:
        if self.__style.visible:
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