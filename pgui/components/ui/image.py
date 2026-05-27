"""
Image Module
============
This module provides a styled image display component
built on top of pygame.

The component supports multiple scaling modes,
optional rounded corner clipping,
background fill,
and border rendering.

It includes:
- `StyleImage` : Dataclass holding all visual
                 and scaling configuration for an image.
- `Image`      : Loads, scales, and renders an image
                 inside a styled rectangular frame.

Typical usage:
>>> style = StyleImage(
        path="assets/avatar.png",
        size=(100, 100),
        pos=(50, 50),
        mode="fit",
        border_radius=12,
        border=2,
        border_color="#aaaaaa"
     )
     image = Image(surface, style)
     # Inside game loop
     image.update()
"""

import pygame

from dataclasses import dataclass

from typing import Optional, Literal, Tuple
from pgui.utils.utils_typing import Vec2, ColorType, Number

from pgui.utils.utils_transform import hex_to_rbg, to_array

@dataclass(slots=True)
class StyleImage:

    """
    Dataclass containing all visual
    and scaling configuration for an Image.

    Scaling modes
    -------------
    The image supports four scaling modes:

    - ``fit`` :
        Scales the image to fit inside the target size while preserving aspect ratio.
        Empty space may remain on one axis.

    - ``fill`` :
        Scales the image to fully cover the target size while preserving aspect ratio.
        Parts of the image may be cropped.

    - ``stretch`` : 
        Scales the image to exactly match the target size. Aspect ratio is not preserved.

    - ``custom`` :
        Uses ``scale`` as a manual scaling multiplier.

    Rendering
    ---------
    The image can optionally render:

    - Background fill
    - Border
    - Rounded corner clipping

    Rounded corners are applied to the rendered image, background, and border.

    Attributes
    ----------
    >>> path : str, optional

        File path of the image to load.

    >>> bg_color : ColorType

        Background color rendered behind the image.

    >>> border : int

        Border thickness in pixels. ``0`` disables border rendering.

    >>> border_color : ColorType

        Color of the border.

    >>> border_radius : int

        Corner radius used for:

            - image clipping
            - background rendering
            - border rendering

    >>> size : Vec2

        Size (width, height) of the image frame.

    >>> pos : Vec2

        Position (x, y) of the image frame on the surface.

    >>> scale : Number

        Manual scale multiplier used when ``mode`` is ``custom``.

    >>> mode : Literal["fit", "fill", "stretch", "custom"]

        Scaling mode applied to the image.

    >>> visible : bool

        Whether the image is rendered. Defaults to True.
    """

    path: Optional[str] = None

    bg_color: ColorType = "#f0f0f0"

    border: int = 0
    border_color: ColorType = "#000000"

    border_radius: int = 0

    size: Vec2 = (100, 100)
    pos: Vec2 = (0, 0)

    scale: Number = 1

    mode: Literal["fit", "fill", "strech", "custome"] = "custome"

    visible: bool = True

class Image:

    """
    A styled image component that loads, scales, and renders an image inside a rectangular frame.

    The component supports:

        - Multiple scaling modes
        - Optional background rendering
        - Optional border rendering
        - Rounded corner clipping

    Initialization
    --------------
    The image is loaded and processed once
    during initialization.

    Processing steps:

    1. Load image from disk

    2. Apply scaling mode

    3. Apply rounded corner clipping
    (if enabled)

    Rendering order (back to front)
    --------------------------------
    1. Border
    (slightly larger rect behind the frame)

    2. Background
    (filled rect at frame position)

    3. Image
    (scaled and clipped image
    centered inside the frame)

    Scaling behavior
    ----------------
    Scaling is handled internally by ``__scale_image()``.

    Depending on the selected mode, the component calculates an appropriate scale ratio or target size.

    Rounded clipping
    ----------------
    Rounded corners are applied using an RGBA mask surface.

    The clipping affects only the rendered image surface.

    Attributes
    ----------
    >>> surface : pygame.Surface

        The surface on which the image is drawn.

    >>> style : StyleImage

        The style/configuration object for this image.

    Methods
    -------
    >>> update() -> None

        Draws the border, background, and image each frame.
        Does nothing if ``StyleImage.visible`` is False.

    Example
    -------
>>> style = StyleImage(
            path="assets/logo.png",
            size=(200, 200),
            pos=(100, 100),
            mode="fit",
            border_radius=16,
            border=2,
            border_color="#cccccc"
        )
        image = Image(surface, style)
        # Inside game loop
        image.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleImage):
        self.__surface = surface
        self.__style = style
        self.__visible = style.visible
        self.__pos = style.pos

        self.__path_image = self.__style.path

        self.__image = pygame.image.load(self.__path_image).convert_alpha()
        self.__scale_image()
        self.__image = self.__apply_border_radius()

        self.__rect = pygame.Rect(self.__pos, self.__style.size)
    
    def get_rect(self) -> pygame.Rect:
        return self.__rect
    
    @property
    def pos(self) -> Vec2:
        return self.__pos

    @pos.setter
    def pos(self, new_pos: Vec2):
        self.__pos = new_pos
    
    @property 
    def path_image(self) -> str:
        return self.__path_image
    
    @path_image.setter
    def path_image(self, path: str):
        self.__path_image = path

    @property
    def visible(self) -> bool:
        return self.__visible
    
    @visible.setter
    def visible(self, value) -> bool:
        self.__visible = value
        
    def update(self):
        if self.__visible:
            self.__draw_border()
            self.__draw_bg()
            self.__draw_image()

    def __draw_bg(self):
        bg = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), bg, border_radius=self.__style.border_radius)
    
    def __draw_border(self):
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2
        pos_border = to_array(self.__pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)
    
    def __draw_image(self):
        image_rect = self.__image.get_rect(center=self.__rect.center)
        self.__surface.blit(self.__image, image_rect)
    
    def __scale_image(self):
        image_size = self.__image.get_size()

        if self.__style.mode == "fill":
            ratio = self.__calc_ratio_fill(image_size, self.__style.size)
        elif self.__style.mode == "fit":
            ratio = self.__calc_ratio_fit(image_size, self.__style.size)
        elif self.__style.mode == "strech":
            self.__image = pygame.transform.scale(self.__image, self.__calc_ratio_stretch(image_size, self.__style.size))
            return
        else: ratio = self.__style.scale
        
        new_size = to_array(image_size) * ratio 
        self.__image = pygame.transform.scale(self.__image, (int(new_size[0]), int(new_size[1])))

    def __apply_border_radius(self) -> pygame.Surface:
        if self.__style.border_radius <= 0: return self.__image

        size = self.__image.get_size()

        result = pygame.Surface(size, pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))

        pygame.draw.rect(
            result,
            (255, 255, 255, 255),
            pygame.Rect((0, 0), size),
            border_radius=self.__style.border_radius
        )

        result.blit(self.__image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        return result

    @staticmethod
    def __calc_ratio_fit(image_size: Vec2, target_size: Vec2) -> float:
        ratio_w = target_size[0] / image_size[0]
        ratio_h = target_size[1] / image_size[1]
        return min(ratio_w, ratio_h)
    
    @staticmethod
    def __calc_ratio_fill(image_size: Vec2, target_size: Vec2) -> float:
        ratio_w = target_size[0] / image_size[0]
        ratio_h = target_size[1] / image_size[1]
        return max(ratio_w, ratio_h)
    
    @staticmethod
    def __calc_ratio_stretch(image_size: Vec2, target_size: Vec2) -> Tuple[Number, Number]:
        return (
            target_size[0] / image_size[0],
            target_size[1] / image_size[1]
        )
