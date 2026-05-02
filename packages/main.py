from __future__ import annotations

import pygame
import numpy as np

from dataclasses import dataclass
from typing import Tuple, Union, List

# ==========================================================
# INIT
# ==========================================================
pygame.init()

# ==========================================================
# TYPE
# ==========================================================
ColorType = Union[str, Tuple[int, int, int]]
Vec2 = Tuple[int, int]


# ==========================================================
# HELPER
# ==========================================================
def _to_color(value: ColorType) -> Tuple[int, int, int]:
    """
    Convert HEX hoặc RGB sang RGB tuple.
    """
    if isinstance(value, tuple):
        return value

    value = value.strip().replace("#", "")

    if len(value) != 6:
        raise ValueError("HEX color must be 6 characters.")

    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _np(value: Vec2) -> np.ndarray:
    """
    Convert tuple -> numpy ndarray
    """
    return np.array(value, dtype=np.int32)


# ==========================================================
# STYLE
# ==========================================================
@dataclass(slots=True)
class StyleTextBox:
    Surface: pygame.Surface
    Content: str = ""

    Font: pygame.font.Font = pygame.font.Font(None, 25)

    Color: ColorType = "#333333"
    Bg_color: ColorType = "#cccccc"

    Antialias: bool = True

    Pos: Vec2 = (0, 0)
    Size: Vec2 = (500, 400)

    Border: int = 0
    Border_radius: int = 0
    Border_color: ColorType = "#000000"

    Padding: int = 0
    Line_height: int = 0

    Visible: bool = True


# ==========================================================
# TEXTBOX
# ==========================================================
class TextBox:
    """
    TextBox hiển thị đoạn văn bản nhiều dòng có auto wrap text.

    Parameters
    ----------
    style : StyleTextBox

        Surface:
            nơi textbox được vẽ lên.

        Content:
            nội dung text cần hiển thị.

        Font:
            pygame.font.Font dùng để render chữ.

        Color:
            màu chữ (HEX hoặc RGB).

        Bg_color:
            màu nền textbox.

        Antialias:
            làm mượt chữ.

        Pos:
            vị trí textbox (x, y).

        Size:
            kích thước textbox (width, height).

        Border:
            độ dày border.

        Border_radius:
            bo góc textbox.

        Border_color:
            màu border.

        Padding:
            khoảng cách text với viền.

        Line_height:
            khoảng cách thêm giữa các dòng.

        Visible:
            có hiển thị hay không.
    """

    def __init__(self, style: StyleTextBox) -> None:
        self.__surface: pygame.Surface = style.Surface
        self.__style: StyleTextBox = style

    # ======================================================
    # PRIVATE
    # ======================================================
    def __wrap_text_box(self) -> List[str]:
        """
        Trả về list dòng text đã wrap.

        Điều kiện:
        chiều rộng mỗi dòng không vượt quá width textbox.
        """
        content: str = self.__style.Content
        font = self.__style.Font

        width_limit = (
            self.__style.Size[0] - self.__style.Padding * 2
        )

        words = content.split(" ")
        lines: List[str] = []

        current_line = ""

        for word in words:
            test_line = word if current_line == "" else current_line + " " + word

            text_width = font.size(test_line)[0]

            if text_width <= width_limit:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def __draw_bg(self) -> None:
        """
        Vẽ background textbox.
        """
        if not self.__style.Visible:
            return

        pos = _np(self.__style.Pos)
        size = _np(self.__style.Size)

        rect = pygame.Rect(
            int(pos[0]),
            int(pos[1]),
            int(size[0]),
            int(size[1]),
        )

        pygame.draw.rect(
            self.__surface,
            _to_color(self.__style.Bg_color),
            rect,
            border_radius=self.__style.Border_radius,
        )

    def __draw_border(self) -> None:
        """
        Vẽ border textbox.
        """
        if not self.__style.Visible:
            return

        if self.__style.Border <= 0:
            return

        pos = _np(self.__style.Pos)
        size = _np(self.__style.Size)

        rect = pygame.Rect(
            int(pos[0]),
            int(pos[1]),
            int(size[0]),
            int(size[1]),
        )

        pygame.draw.rect(
            self.__surface,
            _to_color(self.__style.Border_color),
            rect,
            width=self.__style.Border,
            border_radius=self.__style.Border_radius,
        )

    def __draw_text(self) -> None:
        """
        Vẽ text đã wrap lên textbox.
        """
        if not self.__style.Visible:
            return

        lines = self.__wrap_text_box()

        pos = _np(self.__style.Pos)
        padding = self.__style.Padding

        x = int(pos[0]) + padding
        y = int(pos[1]) + padding

        font = self.__style.Font
        color = _to_color(self.__style.Color)

        line_step = font.get_height() + self.__style.Line_height

        max_height = self.__style.Size[1] - padding

        for line in lines:
            if y + font.get_height() > int(pos[1]) + max_height:
                break

            text_surface = font.render(
                line,
                self.__style.Antialias,
                color
            )

            self.__surface.blit(text_surface, (x, y))

            y += line_step

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self) -> None:
        """
        Cập nhật textbox.
        """
        if not self.__style.Visible:
            return

        self.__draw_bg()
        self.__draw_border()
        self.__draw_text()


# ==========================================================
# DEMO
# ==========================================================
def main() -> None:
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("TextBox Demo")

    clock = pygame.time.Clock()

    content = (
        "Đây là TextBox dùng pygame + numpy. "
        "Text sẽ tự động xuống dòng khi vượt quá chiều rộng của box. "
        "Bạn có thể dùng component này để hiển thị mô tả, log, help text "
        "hoặc chat box đơn giản."
    )

    style = StyleTextBox(
        Surface=screen,
        Content=content,
        Pos=(120, 100),
        Size=(500, 300),
        Padding=15,
        Border=2,
        Border_radius=12,
        Bg_color="#f0f0f0",
        Border_color="#222222",
        Color="#111111",
        Line_height=6,
    )

    textbox = TextBox(style)

    running = True

    while running:
        screen.fill((35, 35, 35))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        textbox.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()