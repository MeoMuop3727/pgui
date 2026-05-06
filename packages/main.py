import pygame
import numpy as np

from dataclasses import dataclass, field
from typing import Literal
from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg


# ==========================================================
# STYLE
# ==========================================================
@dataclass(slots=True)
class StyleTooltip:
    content: str = ""
    placement: Literal["top", "bottom", "left", "right"] = "top"
    offset: Vec2 = (0, 0)

    delay: float = 0.5
    size: Vec2 = (150, 35)

    visible: bool = True

    # bg
    bg_color: ColorType = "#222222"
    border: int = 0
    border_color: ColorType = "#000000"
    border_radius: int = 6

    # text
    color: ColorType = "#ffffff"
    font: pygame.font.Font = field(
        default_factory=lambda: pygame.font.Font(None, 20)
    )
    antialias: bool = True
    padding: int = 8

    # arrow
    show_arrow: bool = True
    arrow_size: Vec2 = (8, 6)
    arrow_color: ColorType = "#222222"


# ==========================================================
# TOOLTIP
# ==========================================================
class Tooltip:
    def __init__(
        self,
        surface: pygame.Surface,
        style: StyleTooltip,
        anchor_rect: pygame.Rect
    ):
        self.__surface = surface
        self.__style = style
        self.__anchor_rect = anchor_rect

        self.__rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

        self.__is_visible: bool = False
        self.__hover_timer: int = 0

        self.__content: str = style.content

    # ======================================================
    # PRIVATE
    # ======================================================
    def __handle_hover(self):
        mouse = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()

        if self.__anchor_rect.collidepoint(mouse):
            if self.__hover_timer == 0:
                self.__hover_timer = now

            elapsed = (now - self.__hover_timer) / 1000.0
            self.__is_visible = elapsed >= self.__style.delay
        else:
            self.__hover_timer = 0
            self.__is_visible = False

    def __calc_pos(self) -> np.ndarray:
        anchor = self.__anchor_rect
        size = to_array(self.__style.size)
        offset = to_array(self.__style.offset)

        if self.__style.placement == "top":
            base = np.array((anchor.centerx - size[0] / 2,
                             anchor.top - size[1]))

        elif self.__style.placement == "bottom":
            base = np.array((anchor.centerx - size[0] / 2,
                             anchor.bottom))

        elif self.__style.placement == "left":
            base = np.array((anchor.left - size[0],
                             anchor.centery - size[1] / 2))

        else:  # right
            base = np.array((anchor.right,
                             anchor.centery - size[1] / 2))

        pos = base + offset

        # clamp vào màn hình
        screen_w, screen_h = self.__surface.get_size()

        pos[0] = max(0, min(screen_w - size[0], pos[0]))
        pos[1] = max(0, min(screen_h - size[1], pos[1]))

        return pos

    def __build_rect(self) -> pygame.Rect:
        pos = self.__calc_pos()
        size = to_array(self.__style.size)

        return pygame.Rect(
            int(pos[0]), int(pos[1]),
            int(size[0]), int(size[1])
        )

    def __draw_bg(self):
        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.bg_color),
            self.__rect,
            border_radius=self.__style.border_radius
        )

    def __draw_border(self):
        if self.__style.border <= 0:
            return

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.border_color),
            self.__rect,
            width=self.__style.border,
            border_radius=self.__style.border_radius
        )

    def __wrap_text(self, text: str) -> list[str]:
        words = text.split(" ")
        lines = []

        max_width = self.__rect.width - self.__style.padding * 2

        current = ""

        for word in words:
            test = current + (" " if current else "") + word
            surf = self.__style.font.render(test, True, (0, 0, 0))

            if surf.get_width() <= max_width:
                current = test
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines

    def __draw_content(self):
        lines = self.__wrap_text(self.__content)

        y = self.__rect.top + self.__style.padding

        for line in lines:
            surf = self.__style.font.render(
                line,
                self.__style.antialias,
                hex_to_rbg(self.__style.color)
            )

            x = self.__rect.left + self.__style.padding

            self.__surface.blit(surf, (x, y))

            y += surf.get_height()

    def __draw_arrow(self):
        if not self.__style.show_arrow:
            return

        base, height = self.__style.arrow_size
        rect = self.__rect
        anchor = self.__anchor_rect

        color = hex_to_rbg(self.__style.arrow_color)

        if self.__style.placement == "top":
            tip = (anchor.centerx, anchor.top)
            points = [
                (tip[0] - base, rect.bottom),
                (tip[0] + base, rect.bottom),
                (tip[0], rect.bottom + height)
            ]

        elif self.__style.placement == "bottom":
            tip = (anchor.centerx, anchor.bottom)
            points = [
                (tip[0] - base, rect.top),
                (tip[0] + base, rect.top),
                (tip[0], rect.top - height)
            ]

        elif self.__style.placement == "left":
            tip = (anchor.left, anchor.centery)
            points = [
                (rect.right, tip[1] - base),
                (rect.right, tip[1] + base),
                (rect.right + height, tip[1])
            ]

        else:  # right
            tip = (anchor.right, anchor.centery)
            points = [
                (rect.left, tip[1] - base),
                (rect.left, tip[1] + base),
                (rect.left - height, tip[1])
            ]

        pygame.draw.polygon(self.__surface, color, points)

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self):
        if not self.__style.visible:
            return

        self.__handle_hover()

        if not self.__is_visible:
            return

        self.__rect = self.__build_rect()

        self.__draw_bg()
        self.__draw_border()
        self.__draw_content()
        self.__draw_arrow()

    @property
    def content(self) -> str:
        return self.__content

    @content.setter
    def content(self, value: str):
        self.__content = value


# ==========================================================
# DEMO
# ==========================================================
if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    anchor = pygame.Rect(350, 250, 100, 60)

    style = StyleTooltip(
        content="This is a tooltip with wrapping text example",
        placement="top",
        size=(180, 60)
    )

    tooltip = Tooltip(screen, style, anchor)

    running = True
    while running:
        screen.fill("#ffffff")

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        pygame.draw.rect(screen, (70, 70, 70), anchor)

        tooltip.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()