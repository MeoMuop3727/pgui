import pygame
import numpy as np

from dataclasses import dataclass
from typing import Optional, Callable, Literal
from enum import Enum

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg


# ==========================================================
# STATE
# ==========================================================
class StateSlider(Enum):
    NORMAL = 1
    HOVER = 2
    PRESSED = 3


# ==========================================================
# STYLE
# ==========================================================
@dataclass(slots=True)
class StyleSlider:
    min_value: float = 0
    max_value: float = 100
    value: float = 0
    step: float = 1

    orientation: Literal["horizontal", "vertical"] = "horizontal"

    size: Vec2 = (200, 20)
    pos: Vec2 = (0, 0)

    visible: bool = True

    on_change: Optional[Callable[[float], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

    # track
    track_color: ColorType = "#cccccc"
    track_color_hover: ColorType = "#bbbbbb"
    track_color_active: ColorType = "#4caf50"

    track_height: int = 6
    track_border_radius: int = 50

    # thumb
    thumb_color: ColorType = "#ffffff"
    thumb_color_hover: ColorType = "#f0f0f0"
    thumb_color_pressed: ColorType = "#e0e0e0"

    thumb_border_color: ColorType = "#aaaaaa"
    thumb_border_color_hover: ColorType = "#888888"
    thumb_border_color_pressed: ColorType = "#555555"

    thumb_size: int = 18
    thumb_border: int = 1
    thumb_border_radius: int = 50


# ==========================================================
# SLIDER
# ==========================================================
class Slider:
    def __init__(self, surface: pygame.Surface, style: StyleSlider):
        self.__surface = surface
        self.__style = style

        self.__value: float = style.value

        self.__is_hovered: bool = False
        self.__is_pressed: bool = False

        self.__track_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.__thumb_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.__fill_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    # ======================================================
    # PRIVATE
    # ======================================================
    def __get_visual_state(self) -> StateSlider:
        if self.__is_pressed:
            return StateSlider.PRESSED
        if self.__is_hovered:
            return StateSlider.HOVER
        return StateSlider.NORMAL

    def __get_thumb_color_state(self):
        state = self.__get_visual_state()

        if state == StateSlider.PRESSED:
            return hex_to_rbg(self.__style.thumb_color_pressed)
        if state == StateSlider.HOVER:
            return hex_to_rbg(self.__style.thumb_color_hover)

        return hex_to_rbg(self.__style.thumb_color)

    def __get_thumb_border_color_state(self):
        state = self.__get_visual_state()

        if state == StateSlider.PRESSED:
            return hex_to_rbg(self.__style.thumb_border_color_pressed)
        if state == StateSlider.HOVER:
            return hex_to_rbg(self.__style.thumb_border_color_hover)

        return hex_to_rbg(self.__style.thumb_border_color)

    def __get_track_color_state(self):
        if self.__is_hovered:
            return hex_to_rbg(self.__style.track_color_hover)
        return hex_to_rbg(self.__style.track_color)

    def __build_track_rect(self) -> pygame.Rect:
        pos = to_array(self.__style.pos)
        size = to_array(self.__style.size)

        if self.__style.orientation == "horizontal":
            track_size = np.array((size[0], self.__style.track_height))
            offset = np.array((0, (size[1] - track_size[1]) // 2))
        else:
            track_size = np.array((self.__style.track_height, size[1]))
            offset = np.array(((size[0] - track_size[0]) // 2, 0))

        final_pos = pos + offset

        return pygame.Rect(
            int(final_pos[0]), int(final_pos[1]),
            int(track_size[0]), int(track_size[1])
        )

    def __calc_thumb_pos(self) -> np.ndarray:
        ratio = (self.__value - self.__style.min_value) / (
            self.__style.max_value - self.__style.min_value
        )

        track = self.__track_rect

        if self.__style.orientation == "horizontal":
            x = track.left + ratio * track.width
            y = track.centery
            return np.array((x, y))

        else:
            y = track.bottom - ratio * track.height
            x = track.centerx
            return np.array((x, y))

    def __build_thumb_rect(self) -> pygame.Rect:
        center = self.__calc_thumb_pos()
        size = self.__style.thumb_size

        pos = center - np.array((size / 2, size / 2))

        return pygame.Rect(int(pos[0]), int(pos[1]), size, size)

    def __build_fill_rect(self) -> pygame.Rect:
        track = self.__track_rect

        if self.__style.orientation == "horizontal":
            width = self.__thumb_rect.centerx - track.left
            return pygame.Rect(track.left, track.top, width, track.height)
        else:
            height = track.bottom - self.__thumb_rect.centery
            return pygame.Rect(track.left, self.__thumb_rect.centery, track.width, height)

    def __calc_value_from_pos(self, mouse_pos: Vec2) -> float:
        track = self.__track_rect

        if self.__style.orientation == "horizontal":
            ratio = (mouse_pos[0] - track.left) / track.width
        else:
            ratio = (track.bottom - mouse_pos[1]) / track.height

        ratio = max(0, min(1, ratio))

        value = self.__style.min_value + ratio * (
            self.__style.max_value - self.__style.min_value
        )

        # step
        step = self.__style.step
        value = round(value / step) * step

        return value

    def __handle_drag(self, events):
        mouse = pygame.mouse.get_pos()

        self.__is_hovered = self.__thumb_rect.collidepoint(mouse)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.__thumb_rect.collidepoint(mouse):
                    self.__is_pressed = True

            elif event.type == pygame.MOUSEBUTTONUP:
                self.__is_pressed = False

        if self.__is_pressed:
            new_value = self.__calc_value_from_pos(mouse)

            if new_value != self.__value:
                self.__value = new_value

                if self.__style.on_change:
                    self.__style.on_change(self.__value)

                if self.__style.on_sound:
                    self.__style.on_sound.play()

    def __draw_track(self):
        pygame.draw.rect(
            self.__surface,
            self.__get_track_color_state(),
            self.__track_rect,
            border_radius=self.__style.track_border_radius
        )

    def __draw_fill(self):
        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.track_color_active),
            self.__fill_rect,
            border_radius=self.__style.track_border_radius
        )

    def __draw_thumb(self):
        pygame.draw.rect(
            self.__surface,
            self.__get_thumb_color_state(),
            self.__thumb_rect,
            border_radius=self.__style.thumb_border_radius
        )

    def __draw_thumb_border(self):
        pygame.draw.rect(
            self.__surface,
            self.__get_thumb_border_color_state(),
            self.__thumb_rect,
            width=self.__style.thumb_border,
            border_radius=self.__style.thumb_border_radius
        )

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self, events):
        if not self.__style.visible:
            return

        self.__track_rect = self.__build_track_rect()
        self.__thumb_rect = self.__build_thumb_rect()
        self.__fill_rect = self.__build_fill_rect()

        self.__handle_drag(events)

        self.__draw_track()
        self.__draw_fill()
        self.__draw_thumb()
        self.__draw_thumb_border()

    def get_value(self) -> float:
        return self.__value

    def set_value(self, value: float):
        self.__value = max(
            self.__style.min_value,
            min(self.__style.max_value, value)
        )


# ==========================================================
# DEMO
# ==========================================================
if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    def on_change(val):
        print("Value:", val)

    style = StyleSlider(
        pos=(300, 250),
        size=(300, 40),
        min_value=0,
        max_value=100,
        value=50,
        on_change=on_change
    )

    slider = Slider(screen, style)

    running = True
    while running:
        screen.fill((30, 30, 30))

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False

        slider.update(events)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()