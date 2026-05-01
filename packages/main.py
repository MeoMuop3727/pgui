from __future__ import annotations

import pygame
import numpy as np

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple, Literal

pygame.init()

# ==========================================================
# TYPE ALIAS
# ==========================================================
ColorType = Tuple[int, int, int] | str
Vec2 = Tuple[int, int]
PaddingType = Tuple[int, int, int, int]  # top left right bottom


# ==========================================================
# HELPER
# ==========================================================
def _to_color(value: ColorType) -> Tuple[int, int, int]:
    """Convert HEX / RGB -> RGB"""
    if isinstance(value, tuple):
        return value

    value = value.replace("#", "")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _np(v: tuple[int, ...]) -> np.ndarray:
    return np.array(v, dtype=np.int32)


# ==========================================================
# STYLE
# ==========================================================
@dataclass
class Style:
    # Tab panel
    Tabs_list: Dict[str, Optional[Callable[[pygame.Surface], None]]] = field(
        default_factory=dict
    )

    # normal
    Color: ColorType = "#000000"
    Bg_color: ColorType = "#ffffff"

    # hover
    Color_hover: ColorType = "#ffffff"
    Bg_color_hover: ColorType = "#444444"

    # pressed
    Color_pressed: ColorType = "#ffffff"
    Bg_color_pressed: ColorType = "#222222"

    # disable
    Color_disable: ColorType = "#888888"
    Bg_color_disable: ColorType = "#cccccc"

    # general
    Font: pygame.font.Font = field(
        default_factory=lambda: pygame.font.Font(None, 20)
    )

    Pos: Vec2 = (0, 0)
    Percent_width_tab_panel: float = 0.35
    Size: Vec2 = (700, 500)

    Border: int = 1
    Border_radius: int = 0
    Border_color: ColorType = "#000000"

    Active_tab: int = 0

    Title: str = ""
    Title_color: ColorType = "#f0f0f0"

    Visible: bool = True

    Padding: PaddingType = (0, 0, 0, 0)


# ==========================================================
# TAB PANEL
# ==========================================================
class TabPanel:
    def __init__(self, surface: pygame.Surface, style: Style):
        self._surface = surface
        self._style = style

        self._hover_index: int = -1

    def _draw_tabs(
        self,
        panel_rect: pygame.Rect,
        vertical: bool = True
    ) -> list[pygame.Rect]:

        tabs = list(self._style.Tabs_list.keys())
        count = len(tabs)

        rects: list[pygame.Rect] = []

        if count == 0:
            return rects

        if vertical:
            tab_h = panel_rect.height // count

            for i, name in enumerate(tabs):
                pos = _np((panel_rect.x, panel_rect.y)) + _np((0, i * tab_h))
                size = _np((panel_rect.width, tab_h))

                rect = pygame.Rect(
                    int(pos[0]), int(pos[1]),
                    int(size[0]), int(size[1])
                )
                rects.append(rect)

                self._draw_single_tab(rect, name, i)

        else:
            tab_w = panel_rect.width // count

            for i, name in enumerate(tabs):
                pos = _np((panel_rect.x, panel_rect.y)) + _np((i * tab_w, 0))
                size = _np((tab_w, panel_rect.height))

                rect = pygame.Rect(
                    int(pos[0]), int(pos[1]),
                    int(size[0]), int(size[1])
                )
                rects.append(rect)

                self._draw_single_tab(rect, name, i)

        return rects

    def _draw_single_tab(
        self,
        rect: pygame.Rect,
        text: str,
        index: int
    ) -> None:

        if index == self._style.Active_tab:
            bg = _to_color(self._style.Bg_color_pressed)
            fg = _to_color(self._style.Color_pressed)

        elif index == self._hover_index:
            bg = _to_color(self._style.Bg_color_hover)
            fg = _to_color(self._style.Color_hover)

        else:
            bg = _to_color(self._style.Bg_color)
            fg = _to_color(self._style.Color)

        pygame.draw.rect(
            self._surface,
            bg,
            rect,
            border_radius=self._style.Border_radius
        )

        if self._style.Border > 0:
            pygame.draw.rect(
                self._surface,
                _to_color(self._style.Border_color),
                rect,
                self._style.Border,
                border_radius=self._style.Border_radius
            )

        text_surface = self._style.Font.render(text, True, fg)
        text_rect = text_surface.get_rect(center=rect.center)
        self._surface.blit(text_surface, text_rect)

    def _on_click(self, mouse_pos: Vec2, rects: list[pygame.Rect]) -> None:
        for i, rect in enumerate(rects):
            if rect.collidepoint(mouse_pos):
                self._style.Active_tab = i
                break

    def update(
        self,
        panel_rect: pygame.Rect,
        vertical: bool,
        events: list[pygame.event.Event]
    ) -> None:

        rects = self._draw_tabs(panel_rect, vertical)

        self._hover_index = -1
        mouse = pygame.mouse.get_pos()

        for i, rect in enumerate(rects):
            if rect.collidepoint(mouse):
                self._hover_index = i

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._on_click(event.pos, rects)


# ==========================================================
# TAB FRAME
# ==========================================================
class TabFrame:
    def __init__(self, surface: pygame.Surface, style: Style):
        self._surface = surface
        self._style = style

    def _draw_frame_content(
        self,
        frame_rect: pygame.Rect
    ) -> None:

        funcs = list(self._style.Tabs_list.values())

        if not funcs:
            return

        idx = self._style.Active_tab

        if idx >= len(funcs):
            return

        func = funcs[idx]

        if func is not None:
            sub = self._surface.subsurface(frame_rect)
            func(sub)

    def update(self, frame_rect: pygame.Rect) -> None:
        pygame.draw.rect(
            self._surface,
            _to_color(self._style.Bg_color),
            frame_rect
        )

        pygame.draw.rect(
            self._surface,
            _to_color(self._style.Border_color),
            frame_rect,
            self._style.Border
        )

        self._draw_frame_content(frame_rect)


# ==========================================================
# TAB
# ==========================================================
class Tab:
    def __init__(
        self,
        tab_type: Literal["vertical", "horizontial"],
        pos_tabpanel: str,
        screen: pygame.Surface,
        style: Style
    ):

        self._type = tab_type
        self._pos_tabpanel = pos_tabpanel
        self._screen = screen
        self._style = style

        self._surface = pygame.Surface(style.Size)

        self._panel = TabPanel(self._surface, style)
        self._frame = TabFrame(self._surface, style)

    def _get_layout(self) -> tuple[pygame.Rect, pygame.Rect]:

        w, h = self._style.Size
        percent = self._style.Percent_width_tab_panel

        if self._type == "horizontial":
            pw = int(w * percent)

            if self._pos_tabpanel == "right":
                panel = pygame.Rect(w - pw, 0, pw, h)
                frame = pygame.Rect(0, 0, w - pw, h)
            else:
                panel = pygame.Rect(0, 0, pw, h)
                frame = pygame.Rect(pw, 0, w - pw, h)

        else:
            ph = int(h * percent)

            if self._pos_tabpanel == "bottom":
                panel = pygame.Rect(0, h - ph, w, ph)
                frame = pygame.Rect(0, 0, w, h - ph)
            else:
                panel = pygame.Rect(0, 0, w, ph)
                frame = pygame.Rect(0, ph, w, h - ph)

        return panel, frame

    def update(self) -> None:
        if not self._style.Visible:
            return

        events = pygame.event.get()

        self._surface.fill((240, 240, 240))

        panel_rect, frame_rect = self._get_layout()

        vertical_tabs = self._type == "horizontial"

        self._panel.update(panel_rect, vertical_tabs, events)
        self._frame.update(frame_rect)

        # title
        if self._style.Title:
            txt = self._style.Font.render(
                self._style.Title,
                True,
                _to_color(self._style.Title_color)
            )
            self._surface.blit(txt, (10, 5))

        self._screen.blit(self._surface, self._style.Pos)

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit


# ==========================================================
# DEMO
# ==========================================================
def draw_home(surface: pygame.Surface):
    font = pygame.font.Font(None, 40)
    txt = font.render("HOME PAGE", True, (0, 0, 0))
    surface.blit(txt, (30, 30))


def draw_profile(surface: pygame.Surface):
    font = pygame.font.Font(None, 40)
    txt = font.render("PROFILE PAGE", True, (0, 0, 0))
    surface.blit(txt, (30, 30))


def draw_setting(surface: pygame.Surface):
    font = pygame.font.Font(None, 40)
    txt = font.render("SETTING PAGE", True, (0, 0, 0))
    surface.blit(txt, (30, 30))


def main():
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()

    style = Style(
        Pos=(100, 80),
        Size=(800, 500),
        Title="My Tab UI",
        Percent_width_tab_panel=0.25,
        Tabs_list={
            "Home": draw_home,
            "Profile": draw_profile,
            "Setting": draw_setting
        },
        Bg_color="#ffffff",
        Bg_color_hover="#3498db",
        Bg_color_pressed="#2c3e50",
        Color="#000000",
        Color_hover="#ffffff",
        Color_pressed="#ffffff",
        Border=1,
        Border_color="#000000",
    )

    tab = Tab(
        tab_type="horizontial",
        pos_tabpanel="left",
        screen=screen,
        style=style
    )

    while True:
        screen.fill((30, 30, 30))

        tab.update()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()