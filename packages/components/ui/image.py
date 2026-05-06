"""
Image Module
============
This module provides a styled image display component built on top of pygame.
It supports multiple scaling modes, optional border radius clipping,
background fill, and border rendering.

It includes:
- `StyleImage` : Dataclass holding all style/configuration options for an image.
- `Image`      : Loads, scales, and renders an image inside a styled rectangular frame.

Typical usage:
    style = StyleImage(
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
from packages.utils.utils_typing import Vec2, ColorType, Number

from packages.utils.utils_transform import hex_to_rbg, to_array

@dataclass(slots=True)
class StyleImage:

    """
    Dataclass containing all visual and scaling configuration for an Image.

    Scaling modes
    -------------
    - ``fit``     : Scales the image to fit within the target size while
                    preserving aspect ratio. May leave empty space on sides.
    - ``fill``    : Scales the image to fill the target size while
                    preserving aspect ratio. May crop the image.
    - ``stretch`` : Scales the image to exactly match the target size.
                    Does not preserve aspect ratio.
    - ``custom``  : Uses the ``scale`` field as a manual ratio multiplier.

    Attributes
    ----------
    path : str, optional
        File path to the image to load. Defaults to None.
    bg_color : ColorType
        Background color shown behind the image. Defaults to #f0f0f0.
    border : int
        Border thickness in pixels. 0 means no border.
    border_color : ColorType
        Color of the border. Defaults to #000000.
    border_radius : int
        Corner radius for rounded clipping applied to the image,
        background, and border. Defaults to 0.
    size : Vec2
        Size (width, height) of the image frame. Defaults to (100, 100).
    pos : Vec2
        Position (x, y) of the image frame on the surface. Defaults to (0, 0).
    scale : Number
        Manual scale ratio used when ``mode`` is ``custom``. Defaults to 1.
    mode : Literal["fit", "fill", "stretch", "custom"]
        Scaling mode applied to the image. Defaults to ``custom``.
    visible : bool
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
    A styled image component that loads, scales, and renders an image
    inside a rectangular frame with optional background, border, and rounded corners.

    The image is loaded, scaled, and border-radius clipped once at initialization.
    On each ``update()`` call, the border, background, and image are drawn in order.

    Scaling
    -------
    Scaling is handled at init time via ``__scale_image()``, which applies
    one of four modes: fit, fill, stretch, or custom ratio.
    The resulting image is then passed through ``__apply_border_radius()``
    to clip rounded corners using an RGBA mask.

    Rendering order (back to front)
    --------------------------------
    1. Border      (slightly larger rect behind the frame)
    2. Background  (filled rect at frame position)
    3. Image       (scaled and clipped, centered within the frame)

    Attributes
    ----------
    surface : pygame.Surface
        The surface on which the image is drawn.
    style : StyleImage
        The style/configuration object for this image.

    Methods
    -------
    update() -> None
        Draws the border, background, and image each frame.
        Does nothing if ``StyleImage.visible`` is False.

    Example
    -------
        style = StyleImage(
            path="assets/logo.png",
            size=(200, 200),
            pos=(100, 100),
            mode="fit",
            border_radius=16,
            border=2,
            border_color="#cccccc"
        )
        
        img = Image(surface, style)

        # Inside game loop
        img.update()
    """

    def __init__(self,
                 surface: pygame.Surface,
                 style: StyleImage):
        self.__surface = surface
        self.__style = style

        self.__image = pygame.image.load(self.__style.path).convert_alpha()
        self.__scale_image()
        self.__image = self.__apply_border_radius()

        self.__rect = pygame.Rect(self.__style.pos, self.__style.size)
    
    def update(self) -> None:
        if self.__style.visible:
            self.__draw_border()
            self.__draw_bg()
            self.__draw_image()

    def __draw_bg(self) -> None:
        bg = self.__rect
        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.bg_color), bg, border_radius=self.__style.border_radius)
    
    def __draw_border(self) -> None:
        border_width: Vec2 = (self.__style.border, self.__style.border)
        size_border = to_array(self.__style.size) + to_array(border_width) * 2
        pos_border = to_array(self.__style.pos) - to_array(border_width)

        border = pygame.Rect(
            (int(pos_border[0]), int(pos_border[1])),
            (int(size_border[0]), int(size_border[1]))
        )

        pygame.draw.rect(self.__surface, hex_to_rbg(self.__style.border_color), border, border_radius=self.__style.border_radius)
    
    def __draw_image(self) -> None:
        image_rect = self.__image.get_rect(center=self.__rect.center)
        self.__surface.blit(self.__image, image_rect)
    
    def __scale_image(self) -> None:
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
