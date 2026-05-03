import pygame

from dataclasses import dataclass
from typing import Optional, Callable, Literal

from packages.utils.utils_typing import Vec2, ColorType
from packages.utils.utils_transform import to_array, hex_to_rbg


# ==========================================================
# STATE
# ==========================================================
class StateSwitch:
    NORMAL = 1
    HOVER = 2
    PRESSED = 3

@dataclass(slots=True)
class StyleSwitch:
    # normal
    track_color: ColorType = "#cccccc"
    thumb_color: ColorType = "#333333"

    # pressed
    track_color_pressed: ColorType = "#333333"
    thumb_color_pressed: ColorType = "#cccccc"

    # hover
    track_color_hover: ColorType = "#333333"
    thumb_color_hover: ColorType = "#cccccc"

    # active
    track_color_active: ColorType = "#333333"
    thumb_color_active: ColorType = "#cccccc"

    # general
    border: int = 0
    border_radius: int = 50
    border_color: ColorType = "#000000"

    on_click: Optional[Callable[[bool], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None

    size: Vec2 = (70, 36)
    pos: Vec2 = (0, 0)

    state: Literal[0, 1] | bool = 0


# ==========================================================
# SWITCH
# ==========================================================
class Switch:
    def __init__(
        self,
        surface: pygame.Surface,
        style: StyleSwitch
    ) -> None:

        self.__surface: pygame.Surface = surface
        self.__style: StyleSwitch = style

        self.__visual_state: int = StateSwitch.NORMAL
        self.__pressed_lock: bool = False

    # ======================================================
    # PRIVATE
    # ======================================================
    def __get_rect(self) -> pygame.Rect:
        pos = to_array(self.__style.pos)
        size = to_array(self.__style.size)

        return pygame.Rect(
            int(pos[0]),
            int(pos[1]),
            int(size[0]),
            int(size[1])
        )

    def __get_state(self) -> bool:
        return bool(self.__style.state)

    def __get_track_color_state(self) -> tuple[int, int, int]:
        active = self.__get_state()

        if self.__visual_state == StateSwitch.PRESSED:
            return hex_to_rbg(self.__style.track_color_pressed)

        if self.__visual_state == StateSwitch.HOVER:
            return hex_to_rbg(self.__style.track_color_hover)

        if active:
            return hex_to_rbg(self.__style.track_color_active)

        return hex_to_rbg(self.__style.track_color)

    def __get_thumb_color_state(self) -> tuple[int, int, int]:
        active = self.__get_state()

        if self.__visual_state == StateSwitch.PRESSED:
            return hex_to_rbg(self.__style.thumb_color_pressed)

        if self.__visual_state == StateSwitch.HOVER:
            return hex_to_rbg(self.__style.thumb_color_hover)

        if active:
            return hex_to_rbg(self.__style.thumb_color_active)

        return hex_to_rbg(self.__style.thumb_color)

    def __draw_track(self) -> None:
        rect = self.__get_rect()

        pygame.draw.rect(
            self.__surface,
            self.__get_track_color_state(),
            rect,
            border_radius=int(rect.height * self.__style.border_radius / 100)
        )

    def __draw_thumb(self) -> None:
        rect = self.__get_rect()

        pad = 4
        thumb_size = rect.height - pad * 2

        if self.__get_state():
            x = rect.right - thumb_size - pad
        else:
            x = rect.left + pad

        y = rect.top + pad

        pygame.draw.circle(
            self.__surface,
            self.__get_thumb_color_state(),
            (x + thumb_size // 2, y + thumb_size // 2),
            thumb_size // 2
        )

    def __draw_border(self) -> None:
        if self.__style.border <= 0:
            return

        rect = self.__get_rect()

        pygame.draw.rect(
            self.__surface,
            hex_to_rbg(self.__style.border_color),
            rect,
            width=self.__style.border,
            border_radius=int(rect.height * self.__style.border_radius / 100)
        )

    def __handle_event(self) -> None:
        rect = self.__get_rect()
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0]

        inside = rect.collidepoint(mouse)

        if inside:
            if pressed:
                self.__visual_state = StateSwitch.PRESSED

                if not self.__pressed_lock:
                    self.__pressed_lock = True
                    self.__style.state = not bool(self.__style.state)

                    if self.__style.on_sound:
                        self.__style.on_sound.play()

                    if self.__style.on_click:
                        self.__style.on_click(bool(self.__style.state))

            else:
                self.__pressed_lock = False
                self.__visual_state = StateSwitch.HOVER

        else:
            self.__pressed_lock = False
            self.__visual_state = StateSwitch.NORMAL

    # ======================================================
    # PUBLIC
    # ======================================================
    def update(self) -> None:
        self.__handle_event()

        self.__draw_track()
        self.__draw_thumb()
        self.__draw_border()

    def get_state(self) -> bool:
        return self.__get_state()


# ==========================================================
# DEMO
# ==========================================================
if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    def on_change(value: bool) -> None:
        print("Switch:", value)

    style = StyleSwitch(
        pos=(300, 250),
        size=(90, 44),
        border=2,
        border_color="#000000",
        on_click=on_change,
        state=0
    )

    switch = Switch(screen, style)

    running = True

    while running:
        screen.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        switch.update()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()