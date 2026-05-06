import pygame
import numpy as np

from dataclasses import dataclass
from typing import Callable, Optional, Literal, List, Tuple, Union

# ==========================================================
# TYPE + UTILS (self-contained)
# ==========================================================
Vec2 = Tuple[int, int]
ColorType = Union[str, Tuple[int, int, int]]


def to_array(v: Vec2) -> np.ndarray:
    return np.array(v, dtype=float)


def hex_to_rbg(color: ColorType) -> Tuple[int, int, int]:
    if isinstance(color, tuple):
        return color
    color = color.lstrip("#")
    return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))


# ==========================================================
# STYLE SCROLL VIEW
# ==========================================================
@dataclass(slots=True)
class StyleScrollView:
    pos: Vec2 = (0, 0)
    size: Vec2 = (300, 300)

    content_size: Vec2 = (300, 800)

    direction: Literal["vertical", "horizontal"] = "vertical"

    scroll_speed: int = 30
    visible: bool = True

    bg_color: ColorType = "#f0f0f0"

    # scrollbar
    show_scrollbar: bool = True
    scrollbar_width: int = 10

    scrollbar_color: ColorType = "#999999"
    scrollbar_color_hover: ColorType = "#777777"
    scrollbar_color_active: ColorType = "#555555"


# ==========================================================
# SCROLL VIEW
# ==========================================================
class ScrollView:
    def __init__(
        self,
        surface: pygame.Surface,
        style: StyleScrollView,
        render_func: Optional[Callable[[pygame.Surface, np.ndarray], None]] = None
    ):
        self.__surface = surface
        self.__style = style
        self.__render_func = render_func

        self.__offset = np.array([0.0, 0.0])

        self.__viewport_rect = pygame.Rect(0, 0, 0, 0)
        self.__scrollbar_rect = pygame.Rect(0, 0, 0, 0)

        self.__dragging = False
        self.__hovered = False

    # ================= PRIVATE =================
    def __build_rect(self):
        pos = to_array(self.__style.pos)
        size = to_array(self.__style.size)

        self.__viewport_rect = pygame.Rect(
            int(pos[0]), int(pos[1]),
            int(size[0]), int(size[1])
        )

    def __handle_wheel(self):
        mouse = pygame.mouse.get_pos()
        if not self.__viewport_rect.collidepoint(mouse):
            return

        for e in pygame.event.get(pygame.MOUSEWHEEL):
            if self.__style.direction == "vertical":
                self.__offset[1] -= e.y * self.__style.scroll_speed
            else:
                self.__offset[0] -= e.y * self.__style.scroll_speed

    def __clamp_offset(self):
        view = to_array(self.__style.size)
        content = to_array(self.__style.content_size)

        max_offset = np.maximum(content - view, 0)
        self.__offset = np.clip(self.__offset, 0, max_offset)

    def __build_scrollbar(self):
        if not self.__style.show_scrollbar:
            return

        view = to_array(self.__style.size)
        content = to_array(self.__style.content_size)

        ratio = view / content

        if self.__style.direction == "vertical":
            height = view[1] * ratio[1]
            y = self.__viewport_rect.top + (self.__offset[1] / content[1]) * view[1]

            self.__scrollbar_rect = pygame.Rect(
                self.__viewport_rect.right - self.__style.scrollbar_width,
                int(y),
                self.__style.scrollbar_width,
                int(height)
            )
        else:
            width = view[0] * ratio[0]
            x = self.__viewport_rect.left + (self.__offset[0] / content[0]) * view[0]

            self.__scrollbar_rect = pygame.Rect(
                int(x),
                self.__viewport_rect.bottom - self.__style.scrollbar_width,
                int(width),
                self.__style.scrollbar_width
            )

    def __handle_drag(self):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        self.__hovered = self.__scrollbar_rect.collidepoint(mouse)

        if pressed and self.__hovered:
            self.__dragging = True

        if not pressed:
            self.__dragging = False

        if self.__dragging:
            view = to_array(self.__style.size)
            content = to_array(self.__style.content_size)

            if self.__style.direction == "vertical":
                rel = mouse[1] - self.__viewport_rect.top
                self.__offset[1] = (rel / view[1]) * content[1]
            else:
                rel = mouse[0] - self.__viewport_rect.left
                self.__offset[0] = (rel / view[0]) * content[0]

    def __draw_bg(self):
        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.bg_color),
            self.__viewport_rect
        )

    def __draw_content(self):
        old_clip = self.__surface.get_clip()
        self.__surface.set_clip(self.__viewport_rect)

        if self.__render_func:
            self.__render_func(self.__surface, self.__offset)

        self.__surface.set_clip(old_clip)

    def __draw_scrollbar(self):
        if not self.__style.show_scrollbar:
            return

        color = self.__style.scrollbar_color

        if self.__dragging:
            color = self.__style.scrollbar_color_active
        elif self.__hovered:
            color = self.__style.scrollbar_color_hover

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(color),
            self.__scrollbar_rect,
            border_radius=5
        )

    # ================= PUBLIC =================
    def update(self):
        if not self.__style.visible:
            return

        self.__build_rect()
        self.__handle_wheel()
        self.__handle_drag()
        self.__clamp_offset()
        self.__build_scrollbar()

        self.__draw_bg()
        self.__draw_content()
        self.__draw_scrollbar()


# ==========================================================
# TEXT FRAME (FOR TEST)
# ==========================================================
class TextFrame:
    def __init__(self, font: pygame.font.Font, color=(0, 0, 0)):
        self.__font = font
        self.__color = color
        self.__lines: List[str] = []

    def __wrap(self, text: str, max_width: int) -> List[str]:
        words = text.split(" ")
        lines = []
        current = ""

        for w in words:
            test = current + (" " if current else "") + w
            if self.__font.render(test, True, self.__color).get_width() <= max_width:
                current = test
            else:
                lines.append(current)
                current = w

        if current:
            lines.append(current)

        return lines

    def set_text(self, text: str, max_width: int):
        self.__lines = self.__wrap(text, max_width)

    def draw(self, surface: pygame.Surface, offset: np.ndarray):
        y = -offset[1]

        for line in self.__lines:
            surf = self.__font.render(line, True, self.__color)
            surface.blit(surf, (10, y))
            y += surf.get_height() + 5


# ==========================================================
# MAIN DEMO
# ==========================================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 24)

    # text dài
    text = ("This is a ScrollView test with wrapped text. " * 40)

    text_frame = TextFrame(font)
    text_frame.set_text(text, 260)

    def render(surface, offset):
        text_frame.draw(surface, offset)

    style = StyleScrollView(
        pos=(250, 100),
        size=(300, 350),
        content_size=(300, 1500)
    )

    scroll = ScrollView(screen, style, render)

    running = True
    while running:
        screen.fill((30, 30, 30))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        scroll.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()