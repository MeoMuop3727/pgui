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

>>> # With branching choices:
>>> manager.push_scence(Dialog(
        surface=screen,
        list_dialogs=["Hello!", "Pick your path!"],
        speed=15,
        stages=["Pick your path!"],
        list_choose={
            "Pick your path!": ["Option 1", "Option 2"]
        },
        new_list_dialog={
            "Option 1": ["You chose Option 1!", "Good luck."],
            "Option 2": ["You chose Option 2!", "Interesting choice."]
        }
    ))
"""

import pygame

from typing import Optional
from pgui.utils.utils_typing import Number

from pgui.components.scenes.scene import Scence
from pgui.components.ui import *
from pgui.utils.utils_transform import to_array

class Dialog(Scence):

    """
    A typewriter-style dialog scene that renders a sequence of text lines
    inside a fixed box anchored to the bottom of the screen.

    Each dialog line is revealed character by character based on ``speed``
    and the delta time passed to ``update()``. Clicking or pressing any key
    advances to the next line. When all lines are exhausted, the scene
    pops itself off the ManageScene stack via ``self.manager.pop_scence()``.

    At designated stage lines (defined by ``stages``), a set of choice buttons
    is displayed. Clicking a button replaces the current dialog sequence with
    the corresponding entry from ``new_list_dialog``, enabling branching narratives.

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
        Defaults to a single empty string if not provided.

>>> speed : Number

        Number of characters revealed per second. Defaults to 10.

>>> stlye_button : StyleButton, optional

        Style configuration for choice buttons.
        Defaults to StyleButton() if not provided.

>>> list_choose : dict[str, list[str]], optional

        Maps a stage dialog line to its list of choice labels.
        Example: { "Pick your path!": ["Option 1", "Option 2"] }

>>> new_list_dialog : dict[str, list[str]], optional

        Maps a choice label to the new dialog sequence to load when that
        choice is selected.
        Example: { "Option 1": ["You chose Option 1!", "Good luck."] }

>>> stages : list[str]

        List of dialog lines that trigger choice buttons.
        When the current dialog line matches an entry in ``stages``,
        the corresponding buttons from ``list_choose`` are shown.

    Methods
    -------
>>> update(delta: float) -> None

        Advances the typewriter effect based on delta time
        and rebuilds the TextBox with the current visible content.

>>> handle_event(events: List[pygame.event.Event]) -> None

        Listens for mouse click or key press to advance to the next
        dialog line or pop the scene when all lines are done.
        Input is ignored when a choice stage is active (``click_transfer = False``).

>>> render(screen: pygame.Surface) -> None

        Clears the screen, draws the dialog box, and updates choice buttons
        if the current line is a stage.

    Example
    -------
>>> manager.push_scence(Dialog(
            surface=screen,
            list_dialogs=["Hello!", "Pick your path!"],
            speed=20,
            stages=["Pick your path!"],
            list_choose={
                "Pick your path!": ["Option 1", "Option 2"]
            },
            new_list_dialog={
                "Option 1": ["You chose Option 1!", "Good luck."],
                "Option 2": ["You chose Option 2!", "Interesting choice."]
            }
        ))
    """

    def __init__(self, 
                 surface: pygame.Surface,
                 font: pygame.font.Font = pygame.font.Font(None, 30),
                 list_dialogs: Optional[list[str]] = None,
                 speed: Number = 10,
                 stlye_button: Optional[StyleButton] = None,
                 list_choose: Optional[dict[str, list[str]]] = None, 
                 new_list_dialog: Optional[dict[str, list[str]]] = None, 
                 stages: list[str] = []):
        super().__init__()

        self.__surface = surface
        self.__font = font
        self.__speed = speed

        self.__box_dialog = TextBox(self.__surface, StyleTextBox())
        self.__current_dialog = 0
        self.__index_text = 0
        self.__list_dialogs = list_dialogs if list_dialogs is not None else [""]
        self.__border_box_dialog = 10
        self.__size_box_dialog = to_array((surface.get_size()[0] - self.__border_box_dialog * 2, 200)) 
        self.__pos_box_dialog = to_array(surface.get_size()) - to_array(self.__size_box_dialog) - to_array((self.__border_box_dialog, self.__border_box_dialog))
        self.__content = ""
        self.__click_transfer = True

        self.__list_choose = list_choose
        self.__new_list_dialog = new_list_dialog
        self.__stages = stages

        self.__style_button = stlye_button if stlye_button is not None else StyleButton()
        self.__list_button: list[ButtonText] = []
    
    def update(self, dental):
        content = self.__load_content()

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
    
    def __event(self):
        content = self.__load_content()
        
        if content in self.__stages: 
            if not self.__list_button:
                self.__list_button = self.__build_list_choose(self.__list_choose[content])
                self.__click_transfer = False

            for button in self.__list_button:
                button.update()
    
    def __load_content(self) -> str:
        try:
            content = self.__list_dialogs[self.__current_dialog]
        except IndexError:
            self.__current_dialog = len(self.__list_dialogs) - 1
            content = self.__list_dialogs[self.__current_dialog]
        return content
    
    def handle_event(self, events):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.__box_dialog.rect.collidepoint(mouse_pos)

        for event in events:
            if is_hover and self.__click_transfer:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.__current_dialog += 1
                    self.__list_button = []
                    if self.__current_dialog < len(self.__list_dialogs):
                        self.__index_text = 0
                    else:
                        self.manager.pop_scence()
    
    def render(self, screen):
        screen.fill("#000000")
        self.__box_dialog.update()
        self.__event()
    
    def __build_list_choose(self, list_choose: Optional[list[str]] = None) -> list[ButtonText]:
        if list_choose is None: return []

        list_button: list[ButtonText] = []

        for index, label in enumerate(list_choose):
            button = ButtonText(self.__surface, self.__style_button)
            button.content = label
            pos_button = (to_array(self.__surface.get_size()) - to_array(button.size)) // 2 + to_array((0, button.size[1])) * index - to_array((0, 100))
            button.pos_button = (int(pos_button[0]), int(pos_button[1]))
            button.on_click_button = lambda l=label: self.__set_new_dialog(l)
            list_button.append(button)
        
        return list_button

    def __set_new_dialog(self, label: str):
        if self.__new_list_dialog is None: return 

        if label in self.__new_list_dialog:
            self.__list_dialogs = self.__new_list_dialog[label]
        self.__current_dialog = 0
        self.__index_text = 0
        self.__click_transfer = True
