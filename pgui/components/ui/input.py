import pygame

from dataclasses import dataclass
from pgui.utils.utils_typing import Vec2, ColorType
from typing import Optional

from pgui.utils.utils_transform import to_array, hex_to_rbg
from enum import Enum

class InputStates(Enum):
    NORMAL = 1
    FOCUSED = 2
    HOVERED = 3

@dataclass(slots=True)
class StyleInput:
    font: pygame.font.Font = pygame.font.Font(None, 25)
    value: str = ""
    placeholder: str = "Placeholder..."
    max_length: int = 100
    visible: bool = True
    size: Vec2 = (350, 65)
    pos: Vec2 = (0, 0)
    color: ColorType = "#333333"
    placeholder_color: ColorType = "#555555"
    background_color: ColorType = "#F0F0F0"
    background_color_hover: ColorType = "#F0F0F0"
    background_color_focused: ColorType = "#F0F0F0"
    border_color: ColorType = "#000000"
    border: int = 0
    border_radius: int = 0
    padding: int = 0
    line_height: int = 5
    cursor_interval: float = 0.5
    allow_numbers: bool = True
    allow_letters: bool = True
    allow_special: bool = True
    password_mode: bool = False

class Input:
    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleInput):
        self.__surface = surface
        self.__style = style
        self.__pos = style.pos 

        self.__rect = pygame.Rect(self.__pos, self.__style.size)

        self.__text = self.__style.placeholder if self.__style.value == "" else self.__style.value

        self.__is_hovered = False
        self.__is_focused = False

        self.__cursor_pos = len(self.__text)
        self.__cursor_visible = False
        self.__cursor_timer = 0
    
    @property
    def pos(self) -> Vec2:
        return self.__pos

    @pos.setter
    def pos(self, new_pos: Vec2):
        self.__pos = new_pos

    @property
    def content(self) -> str:
        return self.__text
    
    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()

        if self.__style.visible:
            self.__is_hovered = self.__rect.collidepoint(mouse_pos)

            if self.__is_hovered and pygame.mouse.get_pressed()[0]:
                if not self.__is_focused:
                    self.__is_focused = True
                    if self.__cursor_pos > 0 and self.__text == self.__style.placeholder: 
                        self.__text = ""
                        self.__cursor_pos = 0
            elif not self.__is_hovered and pygame.mouse.get_pressed()[0]:
                if self.__is_focused:
                    self.__is_focused = False
                    self.__cursor_visible = False
                    if self.__cursor_pos <= 0: 
                        self.__text = self.__style.placeholder
                        self.__cursor_pos = len(self.__text)
            
            if self.__is_focused:
                if now - self.__cursor_timer > self.__style.cursor_interval * 1e3:
                    self.__cursor_visible = not self.__cursor_visible
                    self.__cursor_timer = now

            visual_state = self.__get_visual_state()

            self.__draw_border()
            self.__draw_background(visual_state)
            self.__draw_content()

            if self.__cursor_visible:
                self.__draw_cursor()

    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)

        size_border: Vec2 = to_array(self.__style.size) + to_array(border_width) * 2
        pos: Vec2 = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos[0]), int(pos[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)

    def __draw_background(self, state: InputStates) -> None:
        color = self.__set_background_color(state)
        background = self.__rect

        pygame.draw.rect(self.__surface, hex_to_rbg(color), background, border_radius=self.__style.border_radius)

    def __draw_content(self) -> None:
        lines = self.__wrap_text(self.__text)

        for index, line in enumerate(lines):
            text = line if not self.__style.password_mode else len(line) * "*"
            text_surface = self.__style.font.render(text, True, hex_to_rbg(self.__style.color))
            text_rect = to_array(self.__pos) + to_array((self.__style.padding, self.__style.padding)) + to_array((0, (self.__style.font.get_height() + self.__style.line_height) * index))

            self.__surface.blit(text_surface, (int(text_rect[0]), int(text_rect[1])))
    
    def __draw_cursor(self) -> None:
        WIDTH_CURSOR = 4

        text_before = self.__text[:self.__cursor_pos]
        lines = self.__wrap_text(text_before)

        cursor_line = len(lines) - 1
        cursor_col_text = lines[-1]

        cursor_x = self.__style.font.size(cursor_col_text)[0]
        cursor_y = cursor_line * (self.__style.font.get_height() + self.__style.line_height)

        pos_cursor = to_array(self.__pos) + to_array((self.__style.padding, self.__style.padding)) + to_array((cursor_x, cursor_y))

        cursor = pygame.Rect(
            (int(pos_cursor[0]), int(pos_cursor[1])),
            (WIDTH_CURSOR, self.__style.font.get_height())
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.color), cursor)

    def input(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN: return
        if not self.__is_focused: return 

        # ===== Backspace =====
        if event.key == pygame.K_BACKSPACE:
            if self.__cursor_pos > 0:
                self.__text = self.__text[:self.__cursor_pos - 1] + self.__text[self.__cursor_pos:] 
                self.__cursor_pos -= 1

        # ===== Space =====
        elif event.key == pygame.K_SPACE:
            self.__insert_char(" ")

        # ===== Change the cursor pos =====
        elif event.key == pygame.K_LEFT:
            self.__cursor_pos = max(0, self.__cursor_pos - 1)
        elif event.key == pygame.K_RIGHT:
            self.__cursor_pos = min(len(self.__text), self.__cursor_pos + 1)
        
        # ===== Normal char =====
        elif event.unicode:
            self.__insert_char(event.unicode)
    
    def __wrap_text(self, text: str):
        lines = []
        current = ""

        max_width = self.__style.size[0] - 2 * self.__style.padding

        for char in text:
            if self.__style.font.size(current + char)[0] <= max_width: current += char
            else:
                lines.append(current)
                current = char

        lines.append(current)
        return lines

    def __is_char_valid(self, char: Optional[str] = None) -> bool:
        if char.isdigit(): return self.__style.allow_numbers
        elif char.isalpha(): return self.__style.allow_letters
        return self.__style.allow_special
    
    def __insert_char(self, char: Optional[str] = None) -> None:
        if not char: return
        if len(self.__text) >= self.__style.max_length: return
        if not self.__is_char_valid(char): return

        self.__text = self.__text[:self.__cursor_pos] + char + self.__text[self.__cursor_pos:]
        self.__cursor_pos += 1

    def __set_background_color(self, state: InputStates) -> ColorType:
        if state == InputStates.NORMAL: return self.__style.background_color
        elif state == InputStates.HOVERED: return self.__style.background_color_hover
        return self.__style.background_color_focused

    def __get_visual_state(self) -> InputStates:
        if self.__is_hovered: return InputStates.HOVERED
        elif self.__is_focused: return InputStates.FOCUSED
        return InputStates.NORMAL
    