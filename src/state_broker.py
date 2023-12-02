
from enum import Enum
from loop import Loop
from map import Map
from map_config import MapConfig, get_map_config
from map_gen import MapGen

from menu import MENU_RESULT, LoadMenu, MainMenu, NewMenu, SettingsMenu
from settings import Settings, get_settings


RUN_STATE = Enum('run_state', [
    'MENU',
    'SETTINGS',
    'NEW_GAME',
    'LOAD_GAME',
    'EXIT'
])

class StateBroker:

    __state         : RUN_STATE
    __map_cfg       : MapConfig
    __settings      : Settings
    __gen           : MapGen

    def run(self):
        while self.__state != RUN_STATE.EXIT:
            menu = MainMenu()
            res = menu.show()
            if res == MENU_RESULT.QUIT: self.__state = RUN_STATE.EXIT
            elif res == MENU_RESULT.NEW: self.__state = RUN_STATE.NEW_GAME
            elif res == MENU_RESULT.SETTINGS: self.__state = RUN_STATE.SETTINGS
            elif res == MENU_RESULT.LOAD: self.__state = RUN_STATE.LOAD_GAME
            
            match self.__state:
                case RUN_STATE.SETTINGS:
                    menu = SettingsMenu(self.__settings)
                    menu.show()
                    self.__state = RUN_STATE.MENU
                case RUN_STATE.NEW_GAME:
                    menu = NewMenu(self.__map_cfg, self.__settings)
                    r = menu.show()
                    if r == MENU_RESULT.NEW: 
                        #mp = Map(self.__map_cfg, self.__settings)
                        mp = self.__gen.warp_gen()
                        Loop(mp, self.__map_cfg, self.__settings).run()
                    self.__state = RUN_STATE.MENU
                case RUN_STATE.LOAD_GAME:
                    menu = LoadMenu()
                    r = menu.show(self.__map_cfg)
                    if r == MENU_RESULT.LOAD: 
                        mp = self.__gen.warp_gen()
                        Loop(mp, self.__map_cfg, self.__settings).run()
                    self.__state = RUN_STATE.MENU

    def __init__(self) -> None:
        self.__state = RUN_STATE.MENU
        self.__map_cfg = get_map_config()
        self.__settings = get_settings()
        self.__gen = MapGen(self.__map_cfg, self.__settings)


