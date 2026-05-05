import pygame
import numpy as np

from dataclasses import dataclass, field
from typing import Optional, Callable, List
from enum import Enum

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg


# ==========================================================
# STATE
# ==========================================================
class StateDropdown(Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3
    OPEN = 4


# ==========================================================
# STYLE
# ==========================================================
@dataclass(slots=True)
class StyleDropdown:
    options: List[str] = field(default_factory=list)
    selected_index: int = 0
    placeholder: str = "Select..."

    size: Vec2 = (200, 40)
    pos: Vec2 = (0, 0)

    border: int = 1
    border_radius: int = 4

    max_visible_items: int = 5
    padding: int = 8
    gap: int = 2

    font: pygame.font.Font = field(
        default_factory=lambda: pygame.font.Font(None, 25)
    )

    antialias: bool = True
    visible: bool = True

    on_change: Optional[Callable[[int, str], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

    header_color: ColorType = "#222222"
    header_bg_color: ColorType = "#ffffff"
    header_border_color: ColorType = "#aaaaaa"

    header_bg_color_hover: ColorType = "#f0f0f0"
    header_bg_color_open: ColorType = "#e8e8e8"

    list_bg_color: ColorType = "#ffffff"
    list_border_color: ColorType = "#aaaaaa"

    item_color: ColorType = "#222222"
    item_bg_color: ColorType = "#ffffff"

    item_color_hover: ColorType = "#222222"
    item_bg_color_hover: ColorType = "#e8f0fe"

    item_color_selected: ColorType = "#ffffff"
    item_bg_color_selected: ColorType = "#4caf50"


# ==========================================================
# DROPDOWN
# ==========================================================
class Dropdown:
    def __init__(self, surface: pygame.Surface, style: StyleDropdown):
        self.__surface = surface
        self.__style = style

        self.__is_open = False
        self.__selected_index = style.selected_index

        self.__header_rect = self.__build_header_rect()
        self.__item_rects: List[pygame.Rect] = []

    # ======================================================
    # PRIVATE
    # ======================================================
    def __build_header_rect(self) -> pygame.Rect:
        pos = to_array(self.__style.pos)
        size = to_array(self.__style.size)

        return pygame.Rect(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

    def __build_item_rects(self):
        rects = []
        h = self.__header_rect.height

        for i in range(len(self.__style.options)):
            offset = np.array((0, (i + 1) * h))
            pos = to_array(self.__style.pos) + offset

            rects.append(
                pygame.Rect(int(pos[0]), int(pos[1]), self.__header_rect.width, h)
            )

        return rects

    def __handle_events(self, events):
        mouse = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # click header
                if self.__header_rect.collidepoint(mouse):
                    self.__is_open = not self.__is_open
                    return

                # click item
                if self.__is_open:
                    for i, rect in enumerate(self.__item_rects):
                        if rect.collidepoint(mouse):
                            self.__selected_index = i
                            self.__is_open = False

                            if self.__style.on_change:
                                self.__style.on_change(i, self.__style.options[i])

                            if self.__style.on_sound:
                                self.__style.on_sound.play()

                            return

                # click outside → close
                self.__is_open = False

    def __draw_header(self):
        mouse = pygame.mouse.get_pos()

        if self.__is_open:
            bg = hex_to_rbg(self.__style.header_bg_color_open)
        elif self.__header_rect.collidepoint(mouse):
            bg = hex_to_rbg(self.__style.header_bg_color_hover)
        else:
            bg = hex_to_rbg(self.__style.header_bg_color)

        pygame.draw.rect(
            self.__surface,
            bg,
            self.__header_rect,
            border_radius=self.__style.border_radius
        )

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.header_border_color),
            self.__header_rect,
            self.__style.border,
            border_radius=self.__style.border_radius
        )

        text = (
            self.__style.options[self.__selected_index]
            if self.__style.options
            else self.__style.placeholder
        )

        surf = self.__style.font.render(
            text,
            self.__style.antialias,
            hex_to_rbg(self.__style.header_color)
        )

        self.__surface.blit(
            surf,
            (self.__header_rect.x + self.__style.padding,
             self.__header_rect.y + self.__style.padding)
        )

    def __draw_list(self):
        for i, rect in enumerate(self.__item_rects):
            mouse = pygame.mouse.get_pos()

            if i == self.__selected_index:
                bg = hex_to_rbg(self.__style.item_bg_color_selected)
                fg = hex_to_rbg(self.__style.item_color_selected)
            elif rect.collidepoint(mouse):
                bg = hex_to_rbg(self.__style.item_bg_color_hover)
                fg = hex_to_rbg(self.__style.item_color_hover)
            else:
                bg = hex_to_rbg(self.__style.item_bg_color)
                fg = hex_to_rbg(self.__style.item_color)

            pygame.draw.rect(self.__surface, bg, rect)

            surf = self.__style.font.render(
                self.__style.options[i],
                True,
                fg
            )

            self.__surface.blit(
                surf,
                (rect.x + self.__style.padding,
                 rect.y + self.__style.padding)
            )

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self, events):
        if not self.__style.visible:
            return

        self.__header_rect = self.__build_header_rect()
        self.__item_rects = self.__build_item_rects()

        self.__handle_events(events)

        self.__draw_header()

        if self.__is_open:
            self.__draw_list()

    def get_selected_index(self) -> int:
        return self.__selected_index

    def get_selected_value(self) -> str:
        if not self.__style.options:
            return ""
        return self.__style.options[self.__selected_index]


# ==========================================================
# DEMO
# ==========================================================
if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    def on_change(i, val):
        print("Selected:", i, val)

    style = StyleDropdown(
        pos=(300, 200),
        options=["Python", "C++", "Java", "Rust"],
        on_change=on_change
    )

    dropdown = Dropdown(screen, style)

    running = True

    while running:
        screen.fill((240, 240, 240))

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        dropdown.update(events)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()