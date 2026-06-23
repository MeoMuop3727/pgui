import pygame
from typing import Optional
from pgui.utils.utils_transform import hex_to_rbg
from pgui.utils.utils_typing import Vec2

class BackgroundImage:
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
    def size(self) -> Vec2:
        return self.__background_img.get_size()
    
    @property
    def pos(self) -> Vec2:
        return self.__pos
    
    @pos.setter
    def pos(self, value: Vec2):
        self.__pos = value
        if self.__error_load_img:
            self.__background_img = pygame.Rect(self.__pos, self.__surface.get_size())

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
                self.__surface.blit(self.__background_img, self.__pos)
    
    

