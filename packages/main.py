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
class StateCheckbox(Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3


# ==========================================================
# STYLE
# ==========================================================
@dataclass(slots=True)
class StyleCheckbox:
    # general
    label_list: List[str] = field(default_factory=list)
    size: Vec2 = (200, 40)
    pos: Vec2 = (0, 0)

    border: int = 1
    border_radius: int = 0
    border_color: ColorType = "#aaaaaa"

    padding: int = 4
    gap: int = 8
    line_height: int = 5

    font: pygame.font.Font = field(
        default_factory=lambda: pygame.font.Font(None, 25)
    )

    antialias: bool = True
    visible: bool = True

    checked_list: List[int] = field(default_factory=list)

    on_change: Optional[Callable[[List[bool]], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

    # normal
    bg_color: ColorType = "#ffffff"
    check_color: ColorType = "#333333"
    border_color: ColorType = "#aaaaaa"
    label_color: ColorType = "#222222"

    # hover
    bg_color_hover: ColorType = "#f0f0f0"
    border_color_hover: ColorType = "#888888"
    label_color_hover: ColorType = "#222222"

    # pressed
    bg_color_pressed: ColorType = "#e0e0e0"
    border_color_pressed: ColorType = "#555555"
    label_color_pressed: ColorType = "#222222"

    # checked
    bg_color_checked: ColorType = "#4caf50"
    border_color_checked: ColorType = "#388e3c"
    label_color_checked: ColorType = "#222222"


# ==========================================================
# CHECKBOX
# ==========================================================
class Checkbox:
    def __init__(self, surface: pygame.Surface, style: StyleCheckbox):
        self.__surface: pygame.Surface = surface
        self.__style: StyleCheckbox = style

        self.__states: List[int] = [
            1 if i in style.checked_list else 0
            for i in range(len(style.label_list))
        ]

        self.__hover_index: int = -1
        self.__pressed_index: int = -1

    # ======================================================
    # PRIVATE
    # ======================================================
    def __get_visual_state(self, index: int) -> StateCheckbox:
        if index == self.__pressed_index:
            return StateCheckbox.PRESSED

        if index == self.__hover_index:
            return StateCheckbox.HOVER

        return StateCheckbox.NORMAL

    def __get_bg_color_state(self, state: StateCheckbox, checked: bool):
        if checked:
            return hex_to_rbg(self.__style.bg_color_checked)

        if state == StateCheckbox.PRESSED:
            return hex_to_rbg(self.__style.bg_color_pressed)

        if state == StateCheckbox.HOVER:
            return hex_to_rbg(self.__style.bg_color_hover)

        return hex_to_rbg(self.__style.bg_color)

    def __get_border_color_state(self, state: StateCheckbox, checked: bool):
        if checked:
            return hex_to_rbg(self.__style.border_color_checked)

        if state == StateCheckbox.PRESSED:
            return hex_to_rbg(self.__style.border_color_pressed)

        if state == StateCheckbox.HOVER:
            return hex_to_rbg(self.__style.border_color_hover)

        return hex_to_rbg(self.__style.border_color)

    def __get_check_color_state(self):
        return hex_to_rbg(self.__style.check_color)

    def __draw_box(self, rect: pygame.Rect, color):
        pygame.draw.rect(
            self.__surface,
            color,
            rect,
            border_radius=self.__style.border_radius
        )

    def __draw_border(self, rect: pygame.Rect, color):
        pygame.draw.rect(
            self.__surface,
            color,
            rect,
            width=self.__style.border,
            border_radius=self.__style.border_radius
        )

    def __draw_checkmark(self, rect: pygame.Rect):
        pad = 6
        p1 = (rect.left + pad, rect.centery)
        p2 = (rect.centerx, rect.bottom - pad)
        p3 = (rect.right - pad, rect.top + pad)

        pygame.draw.lines(
            self.__surface,
            self.__get_check_color_state(),
            False,
            [p1, p2, p3],
            3
        )

    def __draw_label(self, text: str, pos: Vec2, color):
        surf = self.__style.font.render(
            text,
            self.__style.antialias,
            color
        )
        self.__surface.blit(surf, pos)

    def __handle_event(self, rects: List[pygame.Rect]):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        self.__hover_index = -1

        for i, rect in enumerate(rects):
            if rect.collidepoint(mouse):
                self.__hover_index = i

                if pressed:
                    self.__pressed_index = i
                else:
                    if self.__pressed_index == i:
                        self.__states[i] = 0 if self.__states[i] else 1

                        if self.__style.on_sound:
                            self.__style.on_sound.play()

                        if self.__style.on_change:
                            self.__style.on_change(
                                [bool(s) for s in self.__states]
                            )

                    self.__pressed_index = -1

                return

        self.__pressed_index = -1

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self):
        if not self.__style.visible:
            return

        base_pos = to_array(self.__style.pos)
        size = to_array(self.__style.size)

        box_size = size[1] - self.__style.padding * 2

        rects: List[pygame.Rect] = []

        for i, label in enumerate(self.__style.label_list):
            offset = np.array([0, i * (size[1] + self.__style.line_height)])

            pos = base_pos + offset + self.__style.padding

            rect = pygame.Rect(
                int(pos[0]),
                int(pos[1]),
                int(box_size),
                int(box_size)
            )

            rects.append(rect)

        self.__handle_event(rects)

        for i, label in enumerate(self.__style.label_list):
            rect = rects[i]

            checked = bool(self.__states[i])
            state = self.__get_visual_state(i)

            bg = self.__get_bg_color_state(state, checked)
            border = self.__get_border_color_state(state, checked)

            if checked:
                label_color = hex_to_rbg(self.__style.label_color_checked)
            elif state == StateCheckbox.HOVER:
                label_color = hex_to_rbg(self.__style.label_color_hover)
            elif state == StateCheckbox.PRESSED:
                label_color = hex_to_rbg(self.__style.label_color_pressed)
            else:
                label_color = hex_to_rbg(self.__style.label_color)

            self.__draw_box(rect, bg)
            self.__draw_border(rect, border)

            if checked:
                self.__draw_checkmark(rect)

            label_pos = (
                rect.right + self.__style.gap,
                rect.top
            )

            self.__draw_label(label, label_pos, label_color)

    def get_checked(self) -> List[bool]:
        return [bool(s) for s in self.__states]


# ==========================================================
# DEMO
# ==========================================================
if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    def on_change(states):
        print(states)

    style = StyleCheckbox(
        label_list=["Option A", "Option B", "Option C"],
        pos=(100, 100),
        checked_list=[1],
        on_change=on_change
    )

    checkbox = Checkbox(screen, style)

    running = True

    while running:
        screen.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        checkbox.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()