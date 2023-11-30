
import math
import pygame
from UI import Label
from colors import Color
from config import Config, get_config
from display import Display, get_display
from map import Map, NGon
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
        map = Map()
        r = self.__cfg.win_dim[0]/self.__map_cfg.map_size.value[0]

        m_x = self.__map_cfg.map_size.value[0]
        m_y = self.__map_cfg.map_size.value[1]

        m_x = 4
        m_y = 1
        a_x = math.cos(math.radians(60))
        a_y = math.sin(math.radians(60))

        for y in range(m_y):
            print()
            for x in range(m_x):
                h:NGon
                cx = (r+(4*r*x))*a_x+(5*(y%2)/3*r)
                cy = (r+(2*r*y))*a_y+((x%2)*5/3*r)
                h=hexagon((cx, cy), r)
                h.draw(self.__cvc, Color.CYAN, False, True)
                self.__prnt(f'| {cx}, {cy} | ({x}, {y})')
                pygame.display.update()
                pygame.event.clear()
            
            

        #base = hexagon((0, 0), r)
        #base.render(self.__cvc, Color.CYAN, False, True)
        pygame.display.update()
        return map

    def warp_gen(self) -> Map:
        self.__dsp.clear()
        self.__prnt('<<<WARP GEN>>>')
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