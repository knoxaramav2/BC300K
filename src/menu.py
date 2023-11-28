
import pygame
from enum import Enum
from UI import *
from UI import Control
from colors import Color
from config import GetConfig
from display import Display


MENU_RESULT = Enum(
    'menu_result', [
        'OK',
        'CANCEL',
        'QUIT'
    ]
)

class Menu (Container):

    __active            : bool
    __ret               : MENU_RESULT

    def __handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.__active = False
                    self._ret = MENU_RESULT.CANCEL

    def __loop(self):
        while self.__active:
            self._display.clear()
            self.__handle_events()
            self.update()
            self._display.render()

    def update(self):
        super().update()

    def show(self):
        self.__loop()
        return self.__ret

    def __init__(self, width=0, height=0, 
                 pos_x=0, pos_y=0, 
                 border_width: int = 3, fg=Color.WHITE, bg=Color.BLACK, 
                 border: Color = Color.LIGHT_GRAY, parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, fg, bg, border, parent)

        self.__active = True
        self.__ret = MENU_RESULT.OK

        self._bounds.centerx = self._display.get_canvas().get_width()/2
        self._bounds.centery = self._display.get_canvas().get_height()/2
        
class LoadMenu(Menu):

    def __init__(self) -> None:
        super().__init__()

class NewMenu(Menu):

    def __init__(self) -> None:
        super().__init__()

class SettingsMenu(Menu):

    def __init__(self) -> None:
        super().__init__()

class MainMenu(Menu):

    def __init__(self) -> None:
        cfg = GetConfig()
        width, height = cfg.win_dim
        super().__init__( width=width, height=height)

        btn_width = 120

        quit = Button(text='QUIT', callback=lambda:print('QUIT'), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        new = Button(text='NEW GAME', callback=lambda:print('NEW GAME'), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        load = Button(text='LOAD GAME', callback=lambda:print('LOAD GAME'), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        settings = Button(text='SETTINGS', callback=lambda:print('SETTINGS GAME'), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        self.insert(new, 0, 0, ALIGN.CENTER)
        self.insert(load, 0, 1, ALIGN.CENTER)
        self.insert(settings, 0, 2, ALIGN.CENTER)
        self.insert(quit, 0, 3, ALIGN.CENTER)

        self.pack()
