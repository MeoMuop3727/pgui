"""
Dialog Module
=============
This module provides a typewriter-style dialog box system built on top of pygame,
designed to be used as a Scene within the ManageScene stack.

Text is revealed character by character at a configurable speed.
Clicking or pressing any key advances to the next dialog line.
When all lines are exhausted, the scene pops itself off the stack automatically.

It includes:
- `Dialog` : A scene that renders a sequence of dialog lines with a typewriter effect.

Typical usage:
>>> dialogs = [
        "Welcome to the game!",
        "Character: Are you ready?",
        "Hero: Let's go!"
    ]

>>> manager.push_scence(Dialog(
        surface=screen,
        list_dialogs=dialogs,
        speed=15
    ))
"""

import pygame

from typing import Optional
from utils.utils_typing import Number

from components.scences.scence import Scence
from components.ui.textbox import *
from components.ui.label import *
from utils.utils_transform import to_array

class Dialog(Scence):

    """
    A typewriter-style dialog scene that renders a sequence of text lines
    inside a fixed box anchored to the bottom of the screen.

    Each dialog line is revealed character by character based on ``speed``
    and the delta time passed to ``update()``. Clicking or pressing any key
    advances to the next line. When all lines are exhausted, the scene
    pops itself off the ManageScene stack via ``self.manager.pop_scence()``.

    The dialog box is positioned and sized automatically based on the surface
    dimensions and the configured border spacing.

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which the dialog box is drawn.

>>> font : pygame.font.Font

        Font used to render dialog text. Defaults to pygame.font.Font(None, 30).

>>> list_dialogs : List[str], optional

        List of dialog lines to display in sequence.
        Defaults to a built-in placeholder list if not provided.

>>> speed : Number

        Number of characters revealed per second. Defaults to 10.

    Methods
    -------
>>> update(delta: float) -> None

        Advances the typewriter effect based on delta time
        and rebuilds the TextBox with the current visible content.

>>> handle_event(events: List[pygame.event.Event]) -> None

        Listens for mouse click or key press to advance to the next
        dialog line or pop the scene when all lines are done.

>>> render(screen: pygame.Surface) -> None
        Draws the dialog box onto the screen each frame.

    Example
    -------
>>> manager.push_scence(Dialog(
            surface=screen,
            list_dialogs=["Hello!", "How are you?"],
            speed=20
        ))
    """

    def __init__(self, 
                 surface: pygame.Surface,
                 font: pygame.font.Font = pygame.font.Font(None, 30),
                 list_dialogs: Optional[list[str]] = None,
                 speed: Number = 10):
        super().__init__()

        self.__surface = surface
        self.__font = font
        self.__speed = speed

        self.__current_dialog = 0
        self.__index_text = 0
        self.__list_dialogs = list_dialogs if list_dialogs is not None else [
            "Welcome to the game!",
            "Character: Are you ready?",
            "Hero: Let's go!"
        ]
        self.__border_box_dialog = 10
        self.__size_box_dialog = to_array((surface.get_size()[0] - self.__border_box_dialog * 2, 200)) 
        self.__pos_box_dialog = to_array(surface.get_size()) - to_array(self.__size_box_dialog) - to_array((self.__border_box_dialog, self.__border_box_dialog))
        self.__content = ""
    
    def update(self, dental):
        try:
            content = self.__list_dialogs[self.__current_dialog]
        except IndexError:
            self.__current_dialog = len(self.__list_dialogs) - 1
            content = self.__list_dialogs[self.__current_dialog]

        if self.__index_text < len(content):
            self.__index_text += dental * self.__speed
            self.__content = self.__list_dialogs[self.__current_dialog][:int(self.__index_text)]

        self.__box_dialog = TextBox(
            self.__surface,
            StyleTextBox(
                content=self.__content,
                size=(int(self.__size_box_dialog[0]), int(self.__size_box_dialog[1])),
                pos=(int(self.__pos_box_dialog[0]), int(self.__pos_box_dialog[1])),
                bg_color="#000000",
                color="#ffffff",
                font=self.__font,
                border=self.__border_box_dialog,
                border_color="#ffffff",
                padding=8
            )
        )
    
    def handle_event(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                self.__current_dialog += 1
                if self.__current_dialog < len(self.__list_dialogs):
                    self.__index_text = 0
                else:
                    self.manager.pop_scence()
    
    def render(self, screen):
        self.__box_dialog.update()
