import pygame
import numpy as np

from dataclasses import dataclass
from typing import Callable, List, Optional

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg


# ==========================================================
# STYLE
# ==========================================================
@dataclass(slots=True)
class StyleGrid:
    rows: int = 3
    cols: int = 3

    pos: Vec2 = (0, 0)
    size: Vec2 = (500, 500)

    gap_row: int = 4
    gap_col: int = 4

    padding: tuple[int, int, int, int] = (0, 0, 0, 0)  # top right bottom left

    border: int = 0
    border_color: ColorType = "#000000"
    border_radius: int = 0

    cell_border: int = 0
    cell_border_color: ColorType = "#cccccc"
    cell_border_radius: int = 0
    cell_bg_color: ColorType = "#ffffff"

    bg_color: ColorType = "#f0f0f0"
    visible: bool = True


# ==========================================================
# CELL
# ==========================================================
class GridCell:
    def __init__(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        style: StyleGrid,
        render_func: Optional[Callable[[pygame.Surface], None]] = None
    ):
        self.__surface = surface
        self.__rect = rect
        self.__style = style
        self.__render_func = render_func

    # ---------------- PRIVATE ----------------
    def __draw_bg(self):
        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.cell_bg_color),
            self.__rect,
            border_radius=self.__style.cell_border_radius
        )

    def __draw_border(self):
        if self.__style.cell_border <= 0:
            return

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.cell_border_color),
            self.__rect,
            width=self.__style.cell_border,
            border_radius=self.__style.cell_border_radius
        )

    def __draw_content(self):
        if not self.__render_func:
            return

        sub = self.__surface.subsurface(self.__rect)
        self.__render_func(sub)

    # ---------------- PUBLIC ----------------
    def update(self):
        self.__draw_bg()
        self.__draw_border()
        self.__draw_content()

    def get_surface(self) -> pygame.Surface:
        return self.__surface.subsurface(self.__rect)

    def set_render(self, func: Callable[[pygame.Surface], None]):
        self.__render_func = func


# ==========================================================
# GRID
# ==========================================================
class Grid:
    def __init__(self, surface: pygame.Surface, style: StyleGrid):
        self.__surface = surface
        self.__style = style

        self.__cells: List[List[GridCell]] = []
        self.__cell_size = np.array((0, 0))

        self.__create_cells()

    # ---------------- PRIVATE ----------------
    def __calc_cell_size(self) -> np.ndarray:
        size = to_array(self.__style.size)
        padding = np.array(self.__style.padding)  # top right bottom left

        inner_w = size[0] - padding[1] - padding[3]
        inner_h = size[1] - padding[0] - padding[2]

        total_gap_w = (self.__style.cols - 1) * self.__style.gap_col
        total_gap_h = (self.__style.rows - 1) * self.__style.gap_row

        cell_w = (inner_w - total_gap_w) / self.__style.cols
        cell_h = (inner_h - total_gap_h) / self.__style.rows

        return np.array((cell_w, cell_h))

    def __calc_cell_pos(self, row: int, col: int) -> np.ndarray:
        base = to_array(self.__style.pos)
        padding = np.array(self.__style.padding)

        cell_size = self.__cell_size

        x = (
            base[0]
            + padding[3]
            + col * (cell_size[0] + self.__style.gap_col)
        )

        y = (
            base[1]
            + padding[0]
            + row * (cell_size[1] + self.__style.gap_row)
        )

        return np.array((x, y))

    def __create_cells(self):
        self.__cells.clear()
        self.__cell_size = self.__calc_cell_size()

        for r in range(self.__style.rows):
            row_cells = []
            for c in range(self.__style.cols):
                pos = self.__calc_cell_pos(r, c)

                rect = pygame.Rect(
                    int(pos[0]),
                    int(pos[1]),
                    int(self.__cell_size[0]),
                    int(self.__cell_size[1])
                )

                row_cells.append(
                    GridCell(self.__surface, rect, self.__style)
                )

            self.__cells.append(row_cells)

    def __draw_bg(self):
        rect = pygame.Rect(
            int(self.__style.pos[0]),
            int(self.__style.pos[1]),
            int(self.__style.size[0]),
            int(self.__style.size[1])
        )

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.bg_color),
            rect,
            border_radius=self.__style.border_radius
        )

    def __draw_border(self):
        if self.__style.border <= 0:
            return

        rect = pygame.Rect(
            int(self.__style.pos[0]),
            int(self.__style.pos[1]),
            int(self.__style.size[0]),
            int(self.__style.size[1])
        )

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.border_color),
            rect,
            width=self.__style.border,
            border_radius=self.__style.border_radius
        )

    def __draw_cells(self):
        for row in self.__cells:
            for cell in row:
                cell.update()

    # ---------------- PUBLIC ----------------
    def update(self):
        if not self.__style.visible:
            return

        self.__draw_bg()
        self.__draw_border()
        self.__draw_cells()

    def get_cell(self, row: int, col: int) -> GridCell:
        return self.__cells[row][col]

    def set_cell_content(self, row: int, col: int, func: Callable[[pygame.Surface], None]):
        self.__cells[row][col].set_render(func)

    def get_cell_surface(self, row: int, col: int) -> pygame.Surface:
        return self.__cells[row][col].get_surface()
    
def main():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    style = StyleGrid(
        rows=3,
        cols=3,
        pos=(150, 50),
        size=(500, 500),
        padding=(10, 10, 10, 10),
        gap_row=5,
        gap_col=5,
        cell_border=1
    )

    grid = Grid(screen, style)

    # demo content
    def make_cell_text(text):
        def render(surface):
            font = pygame.font.Font(None, 30)
            txt = font.render(text, True, (0, 0, 0))
            rect = txt.get_rect(center=surface.get_rect().center)
            surface.blit(txt, rect)
        return render

    for r in range(3):
        for c in range(3):
            grid.set_cell_content(r, c, make_cell_text(f"{r},{c}"))

    running = True
    while running:
        screen.fill((30, 30, 30))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        grid.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()