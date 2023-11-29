

import pygame
from colors import Color
from display import Display, get_display
from map import Map
from map_config import MapConfig
from settings import Settings


class Loop:

    __is_active         : bool = False
    __pause             : bool = True
    __display           : Display
    __config            : MapConfig
    __settings          : Settings
    __map               : Map

    def __handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                match e.key:
                    case pygame.K_ESCAPE: self.__pause = not self.__pause
                    case _:
                        pass
            pass

    def __loop(self):
        while self.__is_active:
            self.__display.clear()

            self.__handle_events()
            
            self.__display.render()

    def run(self):
        self.__is_active = True
        self.__loop()

    def __init__(self, map:Map, cfg:MapConfig, stt:Settings) -> None:
        self.__display = get_display()
        self.__config = cfg
        self.__settings = stt
        self.__map = map