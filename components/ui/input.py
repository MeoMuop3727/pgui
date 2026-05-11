"""
Input Module
============
This module provides a single-line and multi-line text input component built on top of pygame.
It supports keyboard input, cursor navigation, text wrapping, placeholder text,
and configurable character validation.

It includes:
- `InputStates` : Enum defining the visual states of an input field.
- `StyleInput`  : Dataclass holding all style/configuration options for an input field.
- `Input`       : Renders an interactive text input field with cursor and focus management.

Typical usage:
>>> style = StyleInput(
        placeholder="Enter your name...",
        size=(350, 65),
        pos=(100, 100),
        border=2,
        border_color="#aaaaaa"
    )
    input_field = Input(surface, style)
    # Inside game loop
    input_field.update()
    # Inside event loop
    for event in pygame.event.get():
        input_field.input(event)
    # Read current value
    text = input_field.content
"""

import pygame

from dataclasses import dataclass
from utils.utils_typing import Vec2, ColorType
from typing import Optional

from utils.utils_transform import to_array, hex_to_rbg
from enum import Enum

class InputStates(Enum):

    """
    Enum representing the visual states of an Input field.

    States
    ------
    NORMAL : int
        Default state — no interaction is occurring.
    FOCUSED : int
        The input field is active and accepting keyboard input.
    HOVERED : int
        The mouse cursor is hovering over the input field.
    """

    NORMAL = 1
    FOCUSED = 2
    HOVERED = 3

@dataclass(slots=True)
class StyleInput:

    """
    Dataclass containing all visual and behavioral configuration for an Input field.

    Attributes
    ----------
    font : pygame.font.Font
        Font used to render input text and placeholder.
    value : str
        Initial text value of the input field. Defaults to empty string.
    placeholder : str
        Text displayed when the input field is empty and unfocused.
    max_length : int
        Maximum number of characters allowed. Defaults to 100.
    visible : bool
        Whether the input field is rendered and interactive. Defaults to True.
    size : Vec2
        Size (width, height) of the input field.
    pos : Vec2
        Position (x, y) of the input field on the surface.
    color : ColorType
        Text color.
    placeholder_color : ColorType
        Color of the placeholder text.
    background_color : ColorType
        Background color in normal state.
    background_color_hover : ColorType
        Background color when hovered.
    background_color_focused : ColorType
        Background color when focused.
    border_color : ColorType
        Color of the border.
    border : int
        Border thickness in pixels. 0 means no border.
    border_radius : int
        Corner radius for rounded borders.
    padding : int
        Inner spacing between the field edge and the text.
    line_height : int
        Additional spacing between wrapped lines of text.
    cursor_interval : float
        Blink interval of the cursor in seconds. Defaults to 0.5.
    allow_numbers : bool
        Whether numeric characters are accepted. Defaults to True.
    allow_letters : bool
        Whether alphabetic characters are accepted. Defaults to True.
    allow_special : bool
        Whether special characters are accepted. Defaults to True.
    password_mode : bool
        Reserved for future use — intended to mask input as asterisks.
    """

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
    
    """
    An interactive text input field supporting typing, cursor navigation,
    text wrapping, placeholder display, and character validation.

    The field becomes focused when clicked and unfocused when clicking outside.
    While focused, a blinking cursor is displayed and keyboard input is accepted.
    Text is automatically wrapped to fit within the field width minus padding.

    Rendering order (back to front)
    --------------------------------
    1. Border      (slightly larger rect behind the background)
    2. Background  (changes color based on visual state)
    3. Text        (word-wrapped lines with padding offset)
    4. Cursor      (blinking vertical bar at current insert position)

    Attributes
    ----------
>>> surface : pygame.Surface
    
        The surface on which the input field is drawn.
    
>>> style : StyleInput
    
        The style/configuration object for this input field.

    Properties
    ----------
>>> content : str
    
        Returns the current text value of the input field.

    Methods
    -------
>>> update() -> None
    
        Handles mouse focus, cursor blinking, and renders the input field each frame.
        Does nothing if ``StyleInput.visible`` is False.

>>> input(event: pygame.event.Event) -> None
        
        Processes a pygame keyboard event.
        Must be called inside the event loop to handle typing and cursor movement.
        Supports: typing, backspace, space, left/right arrow keys.

    Example
    -------
>>> style = StyleInput(
            placeholder="Search...",
            size=(300, 50),
            border=1,
            border_color="#cccccc",
            background_color_focused="#ffffff"
        )
        field = Input(surface, style)
        # Inside game loop
        field.update()
        # Inside event loop
        for event in pygame.event.get():
            field.input(event)
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleInput):
        self.__surface = surface
        self.__style = style

        self.__rect = pygame.Rect(self.__style.pos, self.__style.size)

        self.__text = self.__style.placeholder if self.__style.value == "" else self.__style.value

        self.__is_hovered = False
        self.__is_focused = False

        self.__cursor_pos = len(self.__text)
        self.__cursor_visible = False
        self.__cursor_timer = 0

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
        pos: Vec2 = to_array(self.__style.pos) - to_array(border_width)

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
            text_rect = to_array(self.__style.pos) + to_array((self.__style.padding, self.__style.padding)) + to_array((0, (self.__style.font.get_height() + self.__style.line_height) * index))

            self.__surface.blit(text_surface, (int(text_rect[0]), int(text_rect[1])))
    
    def __draw_cursor(self) -> None:
        WIDTH_CURSOR = 4

        text_before = self.__text[:self.__cursor_pos]
        lines = self.__wrap_text(text_before)

        cursor_line = len(lines) - 1
        cursor_col_text = lines[-1]

        cursor_x = self.__style.font.size(cursor_col_text)[0]
        cursor_y = cursor_line * (self.__style.font.get_height() + self.__style.line_height)

        pos_cursor = to_array(self.__style.pos) + to_array((self.__style.padding, self.__style.padding)) + to_array((cursor_x, cursor_y))

        cursor = pygame.Rect(
            (int(pos_cursor[0]), int(pos_cursor[1])),
            (WIDTH_CURSOR, self.__style.font.get_height())
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.color), cursor)

    def input(self, event: pygame.event.Event) -> None:
        """
        Process a single pygame keyboard event and update the input text accordingly.

        This method must be called inside the pygame event loop each frame.
        It is a no-op if the field is not focused or the event is not a KEYDOWN event.

        Supported keys
        --------------
        Backspace       : Delete the character immediately before the cursor.
        Space           : Insert a space at the current cursor position.
        Left arrow      : Move the cursor one character to the left.
        Right arrow     : Move the cursor one character to the right.
        Any printable   : Insert the character at the current cursor position,
                          subject to max_length and character validation.

        Parameters
        ----------
        event : pygame.event.Event
            A single event from the pygame event queue.
            Only KEYDOWN events are processed; all others are ignored.

        Example
        -------
            for event in pygame.event.get():
                field.input(event)
        """

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
    