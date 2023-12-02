'''
Primary renderer
'''

import pygame
from config import Config, get_config
from display import Display, get_display
from interface import Renderable
from map_config import MapConfig
from settings import Settings


class Camera:

    __zoom              : float
    __pos               : tuple[float, float]
    
    __dsp               : Display
    __cvc               : pygame.Surface
    __settings          : Settings
    __cfg               : Config
    __map_config        : MapConfig

    def set_pos(self, pos:tuple[float, float]):
        self.__pos = pos

    def inc_pos(self, x:float, y:float):
        self.__pos = (self.__pos[0]+x, self.__pos[1]+y)

    def inc_zoom(self, amt:float):
        self.__zoom += amt

    def draw(self, trg:Renderable):
        trg.render(self.__cvc, self.__pos, self.__zoom)

    def update(self):
        pygame.display.update()

    def __init__(self, stt:Settings, map_cfg:MapConfig):
        self.__dsp = get_display()
        self.__cfg = get_config()
        self.__cvc = self.__dsp.get_canvas()
        self.__map_config = map_cfg
        self.__settings = stt
        self.__pos = (self.__cfg.win_dim[0]/2, self.__cfg.win_dim[1]/2)
        self.__zoom = 1.0