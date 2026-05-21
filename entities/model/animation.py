"""
Animation Module
================
This module provides a sprite-sheet-style animation system built on top of pygame,
designed to load and play frame-by-frame animations from a folder structure.

Each subfolder inside the given root path is treated as a named animation.
Images within each subfolder are loaded in sorted order and cycled through
based on the configured frame speed and delta time.

It includes:
- `Animation` : A component that loads, manages, and renders frame animations.

Typical usage:
>>> anim = Animation(
        surface=screen,
        path_folder="assets/player",
        size=(64, 64),
        pos=(100, 200),
        frame_speed=8
    )

>>> # In your game loop:
>>> anim.update(dt)
>>> # Expected folder structure:
>>> assets/player/
        idle/
            0.png
            1.png
            2.png
        run/
            0.png
            1.png
            2.png

>>> anim.current_animation = "assets/player/run"
"""

import pygame, os

from utils.utils_typing import Vec2, ColorType
from pathlib import Path

from utils.utils_transform import hex_to_rbg

class Animation:

    """
    A frame-by-frame animation component that loads images from a folder
    structure and renders them onto a surface.

    Each direct subfolder of ``path_folder`` is treated as a named animation.
    Images inside each subfolder are loaded in sorted order. The animation
    cycles through frames based on ``frame_speed`` and the delta time passed
    to ``update()``.

    Attributes
    ----------
>>> surface : pygame.Surface

        The surface on which frames are drawn.

>>> path_folder : Path

        Root folder containing animation subfolders.

>>> size : Vec2

        Width and height each frame is scaled to. Defaults to (64, 64).

>>> pos : Vec2

        Position on the surface to draw frames. Defaults to (0, 0).

>>> loop : bool

        Whether the animation loops when it reaches the last frame.
        Defaults to True.

>>> visible : bool

        Whether the animation is rendered. Defaults to True.

>>> frame_speed : int

        Number of frames advanced per second. Defaults to 5.

    Methods
    -------
>>> update(dt: float) -> None

        Advances and renders the current animation frame based on delta time.

>>> draw_rect(debug: bool, color: ColorType) -> None

        Draws the bounding rect for debugging purposes.

>>> print_folder() -> None

        Prints the folder structure under ``path_folder`` to stdout.

>>> print_image() -> None

        Prints all loaded animation keys and their frames to stdout.

>>> print_pos() -> None

        Prints the current position to stdout.

    Example
    -------
>>> anim = Animation(
            surface=screen,
            path_folder="assets/player",
            size=(64, 64),
            pos=(100, 200),
            frame_speed=8
        )
>>> anim.current_animation = "assets/player/run"
>>> anim.update(dt)
    """

    def __init__(self,
                 surface: pygame.Surface,
                 path_folder: Path = "",
                 size: Vec2 = (64,64),
                 pos: Vec2 = (0,0),
                 loop: bool = True,
                 visible: bool = True,
                 frame_speed: int = 12):
        self.__surface = surface
        self.__path = Path(path_folder)
        self.__size = size
        self.__pos = pos 
        self.__loop = loop
        self.__visible = visible
        self.__frame_speed = frame_speed

        self.__rect = pygame.Rect(self.__pos, self.__size)

        self.__list_image = self.__load_image() 

        self.__current_animation = next(iter(self.__list_image), "")
        self.__index_animation = 0.0
        self.__image = ...
    
    @property
    def list_animation(self) -> list[str]:
        return list(self.__list_image.keys())

    @property
    def current_animation(self) -> str:
        return self.__current_animation
    
    @current_animation.setter
    def current_animation(self, new_animation):
        self.__current_animation = new_animation
    
    @property
    def rect(self) -> pygame.Rect:
        return self.__rect
    
    @rect.setter
    def rect(self, new_rect: pygame.Rect):
        self.__rect = new_rect

        self.__rescale_image(self.__rect.size)
    
    @property
    def size(self) -> Vec2:
        return self.__size
    
    @size.setter
    def size(self, new_size: Vec2) -> Vec2:
        self.__size = new_size
        self.__rect = pygame.Rect(self.__pos, self.__size)

        self.__rescale_image(new_size)
    
    @property
    def pos(self) -> Vec2:
        return self.__pos
    
    @pos.setter
    def pos(self, new_pos: Vec2) -> Vec2:
        self.__pos = new_pos
        self.__rect = pygame.Rect(self.__pos, self.__size)
    
    @property
    def list_image(self) -> dict[str, list[pygame.Surface]]:
        return self.__list_image
    
    def update(self, dt: float):
        """
        Advances and renders the current animation frame.

        Skips rendering if ``visible`` is False.

        Parameters
        ----------
        dt : float
            Delta time in seconds since the last frame.
        """

        if self.__visible: self.__animation(dt) 
    
    def flip(self, flip_x: bool = False, flip_y: bool = False):
        """
        Flips all animation frames along the specified axes.

        Parameters
        ----------
        flip_x : bool
            If True, flips frames horizontally (left ↔ right). Defaults to False.
        flip_y : bool
            If True, flips frames vertically (top ↔ bottom). Defaults to False.
        """
        
        for key in self.__list_image:
            self.__list_image[key] = [
                pygame.transform.flip(image, flip_x, flip_y)
                for image in self.__list_image[key]
            ]

    # Debug Funcs
    def draw_rect(self, debug: bool = False, color: ColorType = "#333333"):
        """
        Draws the bounding rect of the animation for debugging.

        Parameters
        ----------
        debug : bool
            If True, draws the rect onto the surface. Defaults to False.
        color : ColorType
            Color of the rect outline. Defaults to ``"#333333"``.
        """

        if debug:
            pygame.draw.rect(self.__surface, hex_to_rbg(color), self.__rect)
    
    def print_folder(self):
        """
        Prints the full folder structure under ``path_folder`` to stdout.
        Useful for verifying that animation folders are loaded correctly.
        """

        for root, dirs, files in os.walk(self.__path):
            print("ROOT: ", root)
            for dir in sorted(dirs): print("DIR: ", dir)
            for file in sorted(files): print("FILE: ", file)
    
    def print_image(self):
        """
        Prints all loaded animation keys and their corresponding
        frame surfaces to stdout.
        """

        items = self.__list_image.items()
        for path, images in items:
            print(path)
            for image in images:
                print(image)
    
    def print_pos(self):
        """
        Prints the current position of the animation to stdout.
        """

        print(f"Pos: (x = {self.__pos[0]}, y = {self.__pos[1]})")

    # Render
    def __load_image(self) -> dict[str, list[pygame.Surface]]:
        if not self.__path.exists(): return []

        list_image: dict[str, list[pygame.Surface]] = {}

        for root, _, files in os.walk(self.__path):
            for file in sorted(files):
                if str(root) not in list_image: list_image[str(root)] = []

                full_path = Path(root) / file
                image = pygame.image.load(full_path).convert_alpha()
                image = pygame.transform.scale(image, self.__size)
                list_image[str(root)].append(image)
        
        return list_image
    
    def __animation(self, dt: float):
        frames = self.__list_image[self.__current_animation]

        self.__index_animation += self.__frame_speed * dt

        if self.__index_animation >= len(frames):
            if self.__loop:
                self.__index_animation = 0
            else:
                self.__index_animation = len(frames) - 1

        self.__image = frames[int(self.__index_animation)]

        self.__surface.blit(self.__image, self.__pos)
    
    def __rescale_image(self, new_size: Vec2):
        for key in self.__list_image:
            self.__list_image[key] = [
                pygame.transform.scale(image, new_size)
                for image in self.__list_image[key]
            ]
