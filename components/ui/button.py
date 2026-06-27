"""
Button Module
=============
This module provides a flexible and extensible button system built on top of pygame.

It includes:
- `StateButton`  : Enum defining the visual states of a button.
- `StyleButton`  : Dataclass holding all style/configuration options for a button.
- `Button`       : Base class providing shared logic (hover, press, state management).
- `ButtonText`   : A button that renders styled text with background and border.
- `ButtonImage`  : A button that renders images based on its current state.

Typical usage:
>>> style = StyleButton(
        content="Start",
        bg_color="#ffffff",
        on_click=lambda: print("clicked")
    )
    button = ButtonText(surface, style)
    # Inside game loop
    button.update()
"""

import pygame

from dataclasses import dataclass
from typing import Optional, Callable
from utils.utils_typing import ColorType, Vec2
from enum import Enum

from utils.utils_transform import hex_to_rbg, to_array

class StateButton(Enum):

    """
    Enum representing the visual states of a button.

    States
    ------
    >>> NORMAL : int

        Default state — no interaction is occurring.

    >>> PRESSED : int

        The button is currently being held down by the mouse.

    >>> DISABLE : int

        The button is inactive and does not respond to any interaction.

    >>> HOVER : int

        The mouse cursor is hovering over the button.
    """

    NORMAL = 1
    PRESSED = 2
    DISABLE = 3
    HOVER = 4

@dataclass(slots=True)
class StyleButton:

    """
    Dataclass containing all visual and behavioral configuration for a button.

    State-based styling
    -------------------
    Each visual property (color, bg_color, border_color, image) has four variants
    corresponding to the button's state:
    - normal
    - hover
    - pressed
    - disable

    Attributes
    ----------
    >>> color : ColorType

        Text color in normal state.

    >>> bg_color : ColorType

        Background color in normal state.

    >>> border_color : ColorType

        Border color in normal state.

    >>> image : pygame.Surface, optional

        Image displayed in normal state (used by ButtonImage).

    >>> color_hover : ColorType

        Text color when hovered.

    >>> bg_color_hover : ColorType

        Background color when hovered.

    >>> border_color_hover : ColorType

        Border color when hovered.

    >>> image_hover : pygame.Surface, optional

        Image displayed when hovered.

    >>> color_pressed : ColorType

        Text color when pressed.

    >>> bg_color_pressed : ColorType

        Background color when pressed.

    >>> border_color_pressed : ColorType

        Border color when pressed.

    >>> image_pressed : pygame.Surface, optional

        Image displayed when pressed.

    >>> color_disable : ColorType

        Text color when disabled.

    >>> bg_color_disable : ColorType

        Background color when disabled.

    >>> border_color_disable : ColorType

        Border color when disabled.

    >>> image_disable : pygame.Surface, optional

        Image displayed when disabled.

    General
    -------

    >>> on_click : Callable, optional

        Callback function triggered when the button is clicked.

    >>> on_sound : pygame.mixer.Sound, optional

        Sound played when the button is clicked.

    >>> on_hover : Callable, optional

        Callback function triggered when the button is hovered.

    >>> state : StateButton

        Initial state of the button.

    >>> visible : bool

        Whether the button is rendered and interactive.

    >>> transition : int

        Transition duration in milliseconds.

    >>> pos : Vec2

        Position (x, y) of the button on the surface.

    >>> size : Vec2

        Size (width, height) of the button.

    >>> border : int

        Border thickness in pixels.

    >>> border_radius : int

        Corner radius for rounded borders.

    >>> font : pygame.font.Font

        Font used to render button text.

    >>> content : str

        Text label displayed on the button.

    >>> antialias : bool

        Whether to apply antialiasing to rendered text.
    """

    # normal
    color: ColorType = "#000000"
    bg_color: ColorType = "#f0f0f0"
    border_color: ColorType = "#000000"
    image: Optional[pygame.Surface] = None

    # hover
    color_hover: ColorType = "#f0f0f0"
    bg_color_hover: ColorType = "#000000"
    border_color_hover: ColorType = "#000000"
    image_hover: Optional[pygame.Surface] = None

    # pressed
    color_pressed: ColorType = "#f0f0f0"
    bg_color_pressed: ColorType = "#000000"
    border_color_pressed: ColorType = "#000000"
    image_pressed: Optional[pygame.Surface] = None

    # disable
    color_disable: ColorType = "#f0f0f0"
    bg_color_disable: ColorType = "#000000"
    border_color_disable: ColorType = "#000000"
    image_disable: Optional[pygame.Surface] = None

    # general
    on_click: Optional[Callable[[], None]] = None
    on_sound: Optional[pygame.mixer.Sound] = None
    on_hover: Optional[Callable[[any], None]] = None
    state: StateButton = StateButton.NORMAL
    visible: bool = True
    transition: int = 0
    pos: Vec2 = (0, 0)
    size: Vec2 = (200, 50)
    border: int = 0
    border_radius: int = 0
    font: pygame.font.Font = pygame.font.Font(None, 25)
    content: str = "Click me!"
    antialias: bool = True

class Button:

    """
    Base class for all button types in the button system.

    Provides shared logic for:
    - hover detection
    - press detection
    - click handling
    - visual state management

    Intended to be subclassed.
    `update()` is a no-op by default and should be overridden.

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which the button is drawn.

    >>> style : StyleButton

        The style/configuration object for this button.

    >>> is_hover : bool

        Whether the mouse is currently hovering over the button.

    >>> is_pressed : bool

        Whether the button is currently being pressed.

    >>> pos : Vec2

        Position (x, y) of the button.

    >>> size : Vec2

        Size (width, height) of the button.

    >>> rect : pygame.Rect

        Bounding rectangle of the button.

    >>> state : StateButton

        Current visual state of the button.

    Properties
    ----------

    >>> pos_button : Vec2

        Gets or sets the button position.

        Notes:
            - Updates rect automatically.

    >>> size_button : Vec2

        Gets or sets the button size.

        Notes:
            - Updates rect automatically.

    >>> rect_button : pygame.Rect

        Gets or sets the button bounding rect directly.

    Methods
    -------

    >>> get_visual_state() -> StateButton

        Returns the current visual state based on:
        - hover state
        - pressed state
        - disable state

    >>> update()

        Base no-op update method.

        Notes:
            - Must be overridden in subclasses.

    Example
    -------

    >>> style = StyleButton(
    ...     pos=(100, 100),
    ...     size=(200, 50)
    ... )
    >>>
    >>> button = ButtonText(surface, style)
    >>>
    >>> # Inside game loop
    >>> button.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleButton):
        self.surface = surface
        self.style = style

        self.is_hover = False
        self.is_pressed = False

        self.pos = self.style.pos
        self.size = self.style.size

        self.rect = pygame.Rect(self.pos, self.size)

        self.state = self.style.state

        self.visible = self.style.visible

        self.on_click = self.style.on_click
    
    @property
    def on_click_button(self):
        if self.on_click is not None:
            self.on_click()
    
    @on_click_button.setter
    def on_click_button(self, func: Optional[Callable[[], None]] = None):
        self.on_click = func
    
    @property
    def visible_button(self) -> bool:
        return self.visible

    @visible_button.setter
    def visible_button(self, new_visible: bool):
        self.visible = new_visible
    
    @property
    def pos_button(self) -> Vec2:
        return self.pos
    
    @pos_button.setter
    def pos_button(self, new_pos: Vec2):
        self.pos = new_pos
        self.rect_button = pygame.Rect(new_pos, self.size)
    
    @property
    def size_button(self) -> Vec2:
        return self.size
    
    @size_button.setter
    def size_button(self, new_size: Vec2):
        self.size = new_size
        self.rect(self.pos, new_size)
    
    @property
    def rect_button(self) -> pygame.Rect:
        return self.rect
    
    @rect_button.setter
    def rect_button(self, new_rect: pygame.Rect):
        self.rect = new_rect
    
    def get_visual_state(self) -> StateButton:
        if self.style.state == StateButton.DISABLE: return StateButton.DISABLE
        elif self.is_hover: return StateButton.HOVER
        elif self.is_pressed: return StateButton.PRESSED
        return StateButton.NORMAL
    
    def update(self): pass

class ButtonText(Button):

    """
    A button that renders styled text with background and border.

    Inherits:
    - hover handling
    - press handling
    - click handling
    - state management

    Rendering order (back to front)
    -------------------------------

    1. Border
        Slightly larger rect behind the button.

    2. Background
        Main button background.

    3. Text
        Centered text rendered inside button rect.

    Methods
    -------

    >>> update() -> None

        Updates interaction state and renders the button.

        Rendering steps:
            1. Border
            2. Background
            3. Text

        Notes:
            - Does nothing if ``style.visible`` is False.
            - Triggers ``on_click`` when released inside button.
            - Plays ``on_sound`` if defined.

    Example
    -------

    >>> style = StyleButton(
    ...     content="Play",
    ...     bg_color="#3a3a3a",
    ...     bg_color_hover="#5a5a5a",
    ...     on_click=lambda: start_game()
    ... )
    >>>
    >>> btn = ButtonText(surface, style)
    >>>
    >>> # Inside game loop
    >>> btn.update()
    """

    def __init__(self,
             surface: pygame.Surface,
             style: StyleButton):
        super().__init__(surface, style)
        self.__content = style.content
    
    @property
    def content(self) -> str:
        return self.__content
    
    @content.setter
    def content(self, new_content: str):
        self.__content = new_content
    
    def update(self):
        if self.style.visible:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hover = self.rect.collidepoint(mouse_pos)

            if self.state == StateButton.DISABLE:
                self.is_hover = False
                self.is_pressed = False
            
            if self.is_hover:
                if self.style.on_hover is not None: self.style.on_hover()
            
            if self.is_hover and pygame.mouse.get_pressed()[0]:
                if not self.is_pressed: self.is_pressed = True
            else:
                if self.is_pressed and self.is_hover:
                    if self.on_click is not None: self.on_click()
                    if self.style.on_sound is not None: self.style.on_sound.play()
                self.is_pressed = False
                        
            visual_state = self.get_visual_state()

            color_bg = self.__get_color_bg_state(visual_state)
            color_text = self.__get_color_text_state(visual_state)
            color_border = self.__get_color_border_state(visual_state)

            self.__draw_border_button(color_border)
            self.__draw_bg_button(color_bg)
            self.__draw_text_button(color_text)

    def __get_color_bg_state(self, state: StateButton) -> ColorType:
        color = None

        if state == StateButton.NORMAL: color = self.style.bg_color
        elif state == StateButton.PRESSED: color = self.style.bg_color_pressed
        elif state == StateButton.HOVER: color = self.style.bg_color_hover
        else: color = self.style.bg_color_disable

        return hex_to_rbg(color)

    def __get_color_text_state(self, state: StateButton) -> ColorType:
        color = None
        
        if state == StateButton.NORMAL: color = self.style.color
        elif state == StateButton.PRESSED: color = self.style.color_pressed
        elif state == StateButton.HOVER: color = self.style.color_hover
        else: color = self.style.color_disable

        return hex_to_rbg(color)

    def __get_color_border_state(self, state: StateButton) -> ColorType:
        color = None
        
        if state == StateButton.NORMAL: color = self.style.border_color
        elif state == StateButton.PRESSED: color = self.style.border_color_pressed
        elif state == StateButton.HOVER: color = self.style.border_color_hover
        else: color = self.style.border_color_disable

        return hex_to_rbg(color)
    
    # Rendering
    def __draw_bg_button(self, color: ColorType):
        button = self.rect
        pygame.draw.rect(self.surface, color, button, border_radius=self.style.border_radius)

    def __draw_text_button(self, color: ColorType):
        text_surface = self.style.font.render(self.__content, self.style.antialias, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.surface.blit(text_surface, text_rect)

    def __draw_border_button(self, color: ColorType):
        border_width: Vec2 = (self.style.border, self.style.border)
        size_border = to_array(self.style.size) + to_array(border_width) * 2
        pos_border = to_array(self.style.pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.surface, color, border, border_radius=self.style.border_radius)

class ButtonImage(Button):

    """
    A button that renders an image based on its current visual state.

    Inherits:
    - hover handling
    - press handling
    - click handling
    - state management

    If the image for the current state is None,
    rendering is skipped.

    Image loading
    -------------

    Images are loaded and scaled to ``self.size``
    on every ``update()`` call.

    Notes:
        - For better performance, pre-load images externally.
        - Cached surfaces are recommended for large UI systems.

    Methods
    -------

    >>> update()

        Updates interaction state and renders image.

        Notes:
            - Does nothing if ``style.visible`` is False.
            - Current image depends on visual state.
            - Image is centered inside button rect.

    Example
    -------

    >>> style = StyleButton(
    ...     image="assets/btn_normal.png",
    ...     image_hover="assets/btn_hover.png",
    ...     image_pressed="assets/btn_pressed.png",
    ...     on_click=lambda: open_menu()
    ... )
    >>>
    >>> btn = ButtonImage(surface, style)
    >>>
    >>> # Inside game loop
    >>> btn.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleButton):
        super().__init__(surface, style)

    def update(self):
        if self.style.visible:
            mouse_pos = pygame.mouse.get_pos()
            self.is_hover = self.rect.collidepoint(mouse_pos)

            if self.state == StateButton.DISABLE:
                self.is_hover = False
                self.is_pressed = False
            
            if self.is_hover and pygame.mouse.get_pressed()[0]:
                if not self.is_pressed: self.is_pressed = True
            else:
                if self.is_pressed and self.is_hover:
                    if self.style.on_click is not None: self.style.on_click()
                    if self.style.on_sound is not None: self.style.on_sound.play()
                self.is_pressed = False
                        
            visual_state = self.get_visual_state()

            image = self.__get_image_button_state(visual_state)

            if image is None: return

            color_border = self.__get_color_border_state(visual_state)
            self.__draw_border_button(color_border)

            image_rect = image.get_rect(center=(self.rect.center))

            self.surface.blit(image, image_rect)

    def __get_image_button_state(self, state: StateButton) -> pygame.Surface:
        if state == StateButton.NORMAL: image = self.__load_image(self.style.image)
        elif state == StateButton.PRESSED: image = self.__load_image(self.style.image_pressed)
        elif state == StateButton.HOVER: image = self.__load_image(self.style.image_hover)
        else: image = self.__load_image(self.style.image_disable)

        return image
    
    def __load_image(self, path: Optional[str]) -> Optional[pygame.Surface]:
        if path is None or path == '': return None

        image = pygame.image.load(path)
        image = pygame.transform.scale(image, self.size)

        return image
    
    def __get_color_border_state(self, state: StateButton) -> ColorType:
        color = None
        
        if state == StateButton.NORMAL: color = self.style.border_color
        elif state == StateButton.PRESSED: color = self.style.border_color_pressed
        elif state == StateButton.HOVER: color = self.style.border_color_hover
        else: color = self.style.border_color_disable

        return hex_to_rbg(color)
    
    def __draw_border_button(self, color: ColorType):
        border_width: Vec2 = (self.style.border, self.style.border)
        size_border = to_array(self.style.size) + to_array(border_width) * 2
        pos_border = to_array(self.style.pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.surface, color, border, border_radius=self.style.border_radius)
