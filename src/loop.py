

import pygame
from display import Display


class Loop:

    __is_active         : bool = False
    __pause             : bool = True

    __display           : Display


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
            self.__handle_events()
            self.__display.clear()

    def run(self):
        self.__is_active = True
        self.__loop()

    def __init__(self) -> None:
        self.__display = Display()