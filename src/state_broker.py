
from enum import Enum
from loop import Loop

from menu import MENU_RESULT, LoadMenu, MainMenu, NewMenu, SettingsMenu


RUN_STATE = Enum('run_state', [
    'MENU',
    'SETTINGS',
    'NEW_GAME',
    'LOAD_GAME',
    'EXIT'
])

class StateBroker:

    __state         : RUN_STATE

    def run(self):
        while self.__state != RUN_STATE.EXIT:
            menu = MainMenu()
            res = menu.show()
            if res == MENU_RESULT.QUIT:
                self.__state == RUN_STATE.EXIT

            match self.__state:
                case RUN_STATE.SETTINGS:
                    menu = SettingsMenu()
                    menu.show()
                    self.__state = RUN_STATE.MENU
                case RUN_STATE.NEW_GAME:
                    menu = NewMenu()
                    if menu.show() == MENU_RESULT.OK:
                        Loop().run()
                    self.__state = RUN_STATE.MENU
                case RUN_STATE.LOAD_GAME:
                    menu = LoadMenu()
                    if menu.show() == MENU_RESULT.OK:
                        Loop().run()
                    self.__state = RUN_STATE.MENU
    
    def __init__(self) -> None:
        self.__state = RUN_STATE.MENU