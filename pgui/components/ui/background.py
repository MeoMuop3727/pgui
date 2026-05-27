"""
A lightweight pygame module for handling and rendering background images.

This module provides the `BackgroundImage` class which supports:
- Loading background images from disk.
- Automatically scaling images to match the screen size.
- Visibility toggling.
- Graceful fallback rendering when image loading fails.

Classes
-------
BackgroundImage
    Render and manage a background image on a pygame surface.

Dependencies
------------
- pygame
- typing.Optional

Examples
--------
Basic usage:

>>> import pygame
>>> from background_image import BackgroundImage

>>> pygame.init()

>>> screen = pygame.display.set_mode((1280, 720))
>>> background = BackgroundImage(
...     screen,
...     "assets/background.png"
... )
... # Game loop rendering:
>>> running = True
>>> while running:
...     for event in pygame.event.get():
...         if event.type == pygame.QUIT:
...             running = False
...     background.update()
...     pygame.display.flip()
... # Toggle visibility:
>>> background.visible = False
>>> background.visible = True
... # Fallback behavior:
>>> background = BackgroundImage(screen, "invalid_path.png")
>>> background.update()

Notes
-----
- Loaded images are automatically scaled to the screen size.
- If the image path is invalid, a fallback rectangle is created
  instead of raising an exception.
- The module is designed for simple 2D pygame projects and UI systems.
"""

import pygame
from typing import Optional
from pgui.utils.utils_transform import hex_to_rbg
from pgui.utils.utils_typing import Vec2

class BackgroundImage:

    """
    A utility class used to manage and render a background image
    onto a pygame surface.

    The class supports:
    - Loading an image from a file path.
    - Automatically scaling the image to match the screen size.
    - Toggling visibility.
    - Fallback rendering when the image cannot be loaded.

    Attributes
    ----------
    visible : bool
        Controls whether the background should be rendered.

    Parameters
    ----------
    surface : pygame.Surface
        The main pygame surface where the background will be drawn.

    path : Optional[str], default=None
        Path to the background image file.

    Notes
    -----
    - If the image file cannot be loaded, the class creates a fallback
      rectangle covering the entire screen.
    - The fallback rectangle is rendered using `pygame.draw.rect`.

    Examples
    --------
    Basic usage:

>>> screen = pygame.display.set_mode((1280, 720))
>>> background = BackgroundImage(screen, "assets/background.png")
... # Rendering inside the game loop:

>>> while True:
...     background.update()
...     pygame.display.flip()
... # Hide the background:
>>> background.visible = False
... # Show the background again:
>>> background.visible = True
    """

    def __init__(self, surface: pygame.Surface, path: Optional[str] = None):
        self.__surface = surface
        self.__visible = True
        self.__error_load_img = False
        self.__pos = (0,0)

        try:
            self.__background_img = pygame.image.load(path)
        except FileNotFoundError:
            self.__background_img = pygame.Rect(self.__pos, surface.get_size())
            self.__error_load_img = True

    @property
    def pos(self) -> Vec2:
        return self.__pos
    
    @pos.setter
    def pos(self, value):
        self.__pos = value

    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value):
        self.__visible = value

    def update(self):
        if self.__visible:
            if self.__error_load_img:
                pygame.draw.rect(self.__surface, hex_to_rbg("#000000"), self.__background_img)
            else: 
                self.__background_img = pygame.transform.scale(self.__background_img, self.__surface.get_size())
                self.__surface.blit(self.__background_img, (0,0))
    
    

