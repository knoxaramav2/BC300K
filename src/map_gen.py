
import math
import random
import time
import pygame
from UI import Label
from colors import Color
from config import Config, get_config
from display import Display, get_display
from map import Cell, Map, NGon
from map_config import MapConfig
from settings import Settings
from shapes import hexagon

class MapGen:
     
    __info          : Label
    __dsp           : Display
    __map_cfg       : MapConfig
    __cfg           : Config
    __settigns      : Settings
    __cvc           : pygame.Surface

    def __prnt(self, txt:str):
        print(txt)
        self.__info.set_text(txt)
        self.__info.update()
        self.__dsp.render()

    def __create_pent_map(self):
        map = Map(self.__map_cfg)

        m_x = self.__map_cfg.map_size.value[0]
        m_y = self.__map_cfg.map_size.value[1]
        r = (self.__cfg.win_dim[0]/m_x)*(4.0/5.0)
        # m_x = 1
        # m_y = 2

        a_x = math.cos(math.radians(60))
        a_y = math.sin(math.radians(60))
        dx = 0
        dy = (5.0/6.0)*r

        for y in range(m_y):
            clrb = random.choice(list(Color))
            clrf = random.choice(list(Color))
            print()
            for x in range(m_x):
                cx = (r+(3*r*x))*a_x+((y%2-1)*dx)
                cy = (r+(2*r*y))*a_y+((x%2)*dy)-(2*r)
                
                h=hexagon((cx, cy), r)
                if x > 0:
                    last = map.get(x-1, y)
                    last.add_neighbor(h, 30)
                if y > 0:
                    last = map.get(x, y-1)
                    last.add_neighbor(h, 30)
                map.set(h, x, y)

            self.__prnt(f'| {cx}, {cy} | ({x}, {y})')
            pygame.event.clear()
        self.__dsp.clear()
        map.draw()
        pygame.display.update()
        return map

    def warp_gen(self) -> Map:
        self.__dsp.clear()
        self.__prnt('<<<WARP GEN>>>')
        self.__dsp.clear()
        map = self.__create_pent_map()
        self.__prnt('<<<DONE>>>')
        return map

    def __init__(self, map_config:MapConfig, stt:Settings):
        self.__info = Label(fg=Color.ORANGE, pos_y=20, pos_x=250, width=500, border_width=0, bg=Color.RED)
        self.__map_cfg = map_config
        self.__cfg = get_config()
        self.__settigns = stt  
        self.__dsp = get_display()
        self.__cvc = self.__dsp.get_canvas()