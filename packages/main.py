import pygame
pygame.init()

from dataclasses import dataclass
from typing import Optional, Literal

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg
from packages.components.ui import (
    ButtonText,
    StyleButton,
    TextBox,
    StyleTextBox,
)


# ==========================================================
# STYLE ALERT
# ==========================================================
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

    per_height_title_frame: float = 0.25

    # normal
    button_color: ColorType = "#333333"
    button_bg_color: ColorType = "#ffb3b3"

    # pressed
    button_color_pressed: ColorType = "#ffffff"
    button_bg_color_pressed: ColorType = "#ff884d"

    # hover
    button_color_hover: ColorType = "#ffffff"
    button_bg_color_hover: ColorType = "#ff884d"


# ==========================================================
# ALERT
# ==========================================================
class Alert:
    def __init__(
        self,
        surface: pygame.Surface,
        style: StyleAlert
    ) -> None:

        self.__surface: pygame.Surface = surface
        self.__style: StyleAlert = style

        self.__visible: bool = True

        self.__button_close = self.__create_button()

    # ======================================================
    # PRIVATE
    # ======================================================
    def __get_type_color(self) -> tuple[int, int, int]:
        if self.__style.type == "error":
            return hex_to_rbg("#e74c3c")

        if self.__style.type == "warning":
            return hex_to_rbg("#f39c12")

        if self.__style.type == "success":
            return hex_to_rbg("#27ae60")

        return hex_to_rbg("#3498db")  # info

    def __get_rect(self) -> pygame.Rect:
        pos = to_array(self.__style.pos)
        size = to_array(self.__style.size)

        return pygame.Rect(
            int(pos[0]),
            int(pos[1]),
            int(size[0]),
            int(size[1]),
        )

    def __create_button(self) -> ButtonText:
        rect = self.__get_rect()

        title_h = int(rect.height * self.__style.per_height_title_frame)

        button_size = (40, title_h - 10)

        button_pos = (
            rect.right - button_size[0] - 5,
            rect.top + 5
        )

        style_btn = StyleButton(
            content="X",
            pos=button_pos,
            size=button_size,
            bg_color=self.__style.button_bg_color,
            color=self.__style.button_color,

            bg_color_hover=self.__style.button_bg_color_hover,
            color_hover=self.__style.button_color_hover,

            bg_color_pressed=self.__style.button_bg_color_pressed,
            color_pressed=self.__style.button_color_pressed,

            border=0,
            border_radius=6,
            on_click=self.__close_alert
        )

        return ButtonText(self.__surface, style_btn)

    def __close_alert(self) -> None:
        self.__visible = False

    def __draw_title_frame(self) -> None:
        rect = self.__get_rect()

        title_h = int(rect.height * self.__style.per_height_title_frame)

        title_rect = pygame.Rect(
            rect.x,
            rect.y,
            rect.width,
            title_h
        )

        color = (
            hex_to_rbg(self.__style.bg_title_color)
            if self.__style.bg_title_color
            else self.__get_type_color()
        )

        pygame.draw.rect(
            self.__surface,
            color,
            title_rect
        )

        font = pygame.font.Font(None, 28)

        text = font.render(
            self.__style.title,
            True,
            hex_to_rbg(self.__style.title_color)
        )

        text_rect = text.get_rect(
            midleft=(title_rect.x + 10, title_rect.centery)
        )

        self.__surface.blit(text, text_rect)

    def __draw_content_frame(self) -> pygame.Surface:
        rect = self.__get_rect()

        title_h = int(rect.height * self.__style.per_height_title_frame)

        content_rect = pygame.Rect(
            rect.x,
            rect.y + title_h,
            rect.width,
            rect.height - title_h
        )

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.bg_content_color),
            content_rect
        )

        return content_rect

    def __draw_text_box(self) -> None:
        rect = self.__get_rect()

        title_h = int(rect.height * self.__style.per_height_title_frame)

        padding = self.__style.padding

        tb_pos = (
            rect.x + padding,
            rect.y + title_h + padding
        )

        tb_size = (
            rect.width - padding * 2,
            rect.height - title_h - padding * 2
        )

        style_tb = StyleTextBox(
            content=self.__style.content,
            pos=tb_pos,
            size=tb_size,
            padding=0,
            border=0,
            bg_color=self.__style.bg_content_color,
            color=self.__style.text_color,
            line_height=self.__style.line_height
        )

        textbox = TextBox(self.__surface, style_tb)
        textbox.update()

    def __draw_border(self) -> None:
        if self.__style.border <= 0:
            return

        rect = self.__get_rect()

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.border_color),
            rect,
            width=self.__style.border
        )

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self) -> None:
        if not self.__visible:
            return

        self.__draw_title_frame()
        self.__draw_content_frame()
        self.__draw_text_box()
        self.__draw_border()

        self.__button_close.update()


# ==========================================================
# DEMO
# ==========================================================
if __name__ == "__main__":

    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()

    style = StyleAlert(
        title="Thông Báo",
        content=(
            "Đây là nội dung cảnh báo.\n"
            "Component Alert được tạo từ ButtonText + TextBox.\n"
            "Nhấn nút X để đóng."
        ),
        type="warning",
        pos=(250, 180),
        size=(500, 280),
        border=2,
        border_color="#000000",
        padding=15,
        line_height=5
    )

    alert = Alert(screen, style)

    running = True

    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        alert.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()