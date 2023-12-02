

import pygame
from camera import Camera
from colors import Color
from display import Display, get_display
from map import Map, Vertex
from map_config import MapConfig
from settings import Settings

class Loop:

    __is_active         : bool = False
    __pause             : bool = True
    __display           : Display
    __config            : MapConfig
    __settings          : Settings
    __map               : Map
    __camera            : Camera
    __cvc               : pygame.Surface

    __sel_vert          : Vertex = None

    def __handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                match e.key:
                    case pygame.K_ESCAPE: self.__pause = not self.__pause
                    case _:
                        pass
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                self.__sel_vert = self.__map.select_fuzzed(mx, my)
                print(f'Click: {mx}, {my} | {self.__sel_vert != None}')
            elif e.type == pygame.MOUSEBUTTONUP:
                self.__sel_vert = None
            elif e.type == pygame.MOUSEMOTION:
                if self.__sel_vert == None: break
                self.__sel_vert.pos = (e.pos[0], e.pos[1])
                print(f'M: {e.pos[0]}, {e.pos[1]}')
            elif e.type == pygame.MOUSEWHEEL:
                print(e.y)
                self.__camera.inc_zoom(e.y)

    def __render(self):
        self.__camera.draw(self.__map)

    def __loop(self):
        while self.__is_active:
            self.__display.clear()
            self.__handle_events()
            self.__render()
            self.__camera.update()

    def run(self):
        self.__display.clear()
        self.__is_active = True
        self.__loop()

    def __init__(self, map:Map, cfg:MapConfig, stt:Settings) -> None:
        self.__display = get_display()
        self.__cvc = self.__display.get_canvas()
        self.__config = cfg
        self.__settings = stt
        self.__map = map
        self.__camera = Camera(stt, cfg)

