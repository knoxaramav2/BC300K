
from enum import Enum

import pygame

from UI import Control
from display import Display


MENU_RESULT = Enum(
    'menu_result', [
        'OK',
        'CANCEL',
        'QUIT'
    ]
)

class Menu (Control):

    __active            : bool
    __ret               : MENU_RESULT
    __children          : list[Control]

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
        for c in self.__children:
            c.update()

    def show(self):
        self.__loop()
        return self.__ret

    def __init__(self) -> None:
        super().__init__()
        self.__children = []
        self.__active = True
        self.__ret = MENU_RESULT.OK
        
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
        super().__init__()


