import pygame

from typing import Optional
from pgui.utils.utils_typing import ColorType, Number

from pgui.components.scenes.scene import Scene
from .textbox import TextBox, StyleTextBox
from .button import ButtonText, StyleButton
from .background import BackgroundImage
from pgui.utils.utils_transform import to_array

class Dialog(Scene):
    def __init__(self, 
                 surface: pygame.Surface,
                 font: pygame.font.Font = pygame.font.Font(None, 30),
                 bg_color: ColorType = "#000000",
                 color_font: ColorType = "#ffffff",
                 border_color: ColorType = "#ffffff",
                 list_dialogs: Optional[list[str]] = None,
                 speed: Number = 10,
                 style_button: Optional[StyleButton] = None,
                 list_choose: Optional[dict[str, list[str]]] = None, 
                 new_list_dialog: Optional[dict[str, list[str]]] = None, 
                 stages: list[str] = [],
                 background_image: Optional[BackgroundImage] = None):
        super().__init__()

        self.__surface = surface
        self.__bg_image = background_image

        self.__font = font
        self.__bg_color = bg_color
        self.__color_font = color_font
        self.__border_color = border_color
        self.__speed = speed

        self.__box_dialog = TextBox(self.__surface, StyleTextBox())
        self.__current_dialog = 0
        self.__index_text = 0
        self.__list_dialogs = list_dialogs if list_dialogs is not None else [""]
        self.__border_box_dialog = 10
        self.__size_box_dialog = to_array((surface.get_size()[0] - self.__border_box_dialog * 2, 200)) 
        self.__pos_box_dialog = to_array(surface.get_size()) - to_array(self.__size_box_dialog) \
                                - to_array((self.__border_box_dialog, self.__border_box_dialog))
        self.__content = ""
        self.__click_transfer = True

        self.__list_choose = list_choose
        self.__new_list_dialog = new_list_dialog
        self.__stages = stages

        self.__style_button = style_button if style_button is not None else StyleButton()
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
                bg_color=self.__bg_color,
                color=self.__color_font,
                font=self.__font,
                border=self.__border_box_dialog,
                border_color=self.__border_color,
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
                        self.manager.pop_scene()
    
    def render(self, screen):
        if self.__bg_image is None: screen.fill("#000000")
        else: self.__bg_image.update()
        
        self.__box_dialog.update()
        self.__event()
    
    def __build_list_choose(self, list_choose: Optional[list[str]] = None) -> list[ButtonText]:
        if list_choose is None: return []

        list_button: list[ButtonText] = []

        for index, label in enumerate(list_choose):
            button = ButtonText(self.__surface, self.__style_button)
            button.content = label
            pos_button = (to_array(self.__surface.get_size()) - to_array(button.size)) // 2 \
                            + to_array((0, button.size[1])) * index - to_array((0, 100))
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
