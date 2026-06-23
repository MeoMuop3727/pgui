import pygame, numpy
import pygame.surfarray as surfarray

from numpy.typing import NDArray
from pgui.utils.utils_typing import Vec2

from pgui.utils.utils_transform import to_array

class DrawSystem:
    def __init__(self,
                 surface: pygame.Surface,
                 colors: NDArray[numpy.uint8],
                 matrix: NDArray[numpy.uint8],
                 pos: Vec2 = (0,0),
                 scale: int = 1,
                 disabled: bool = False):
        # Surface
        self.__surface = surface

        # Set up
        self.__pos = pos
        self.__scale = (scale, scale)
        self.__disabled = disabled
        self.__colors = colors
        self.__matrix = matrix

        # Image
        self.__rgb_array = self.__colors[self.__matrix]
        self.__img_surface = surfarray.make_surface(self.__rgb_array.swapaxes(0,1))
        self.__img_size_scale = to_array(self.__img_surface.get_size()) + to_array(self.__scale)
        self.__img_surface = pygame.transform.scale(self.__img_surface, (
            int(self.__img_size_scale[0]), int(self.__img_size_scale[1])
        ))

        # Rect
        self.__rect = pygame.Rect(self.__pos, self.__img_surface.get_size())

        # Buffer
        self.__dirty = False

    def update(self) -> None:
        try:
            if self.__disabled: return

            if self.__dirty:
                self.__rebuild_img()

            self.__render_image()
        except Exception:
            pass

    def get_rect(self) -> pygame.Rect:
        return self.__rect
    
    def set_pos(self, new_pos: Vec2) -> None:
        self.__pos = new_pos
        self.__rect.topleft = new_pos

    def set_dirty(self, value: bool) -> None:
        self.__dirty = value
    
    # --- Rendering ---
    def __render_image(self) -> None:
        self.__surface.blit(self.__img_surface, self.__pos)

    def __rebuild_img(self) -> None:
        self.__rgb_array = self.__colors[self.__matrix]
        self.__img_surface = surfarray.make_surface(self.__rgb_array.swapaxes(0,1))
        self.__img_size_scale = to_array(self.__img_surface.get_size()) + to_array(self.__scale)
        self.__img_surface = pygame.transform.scale(self.__img_surface, (
            int(self.__img_size_scale[0]), int(self.__img_size_scale[1])
        ))
        self.__dirty = False