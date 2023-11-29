from enum import Enum

import pygame
from UI import Label
from colors import Color
from config import Config, get_config
from display import Display, get_display
from map_config import MapConfig
from settings import Settings

CLIMATE = Enum('climate',[
    'POLAR' ,'TEMPERATE' ,'DRY' ,'TROPICAL'
])

class Cell:

    _pos                : tuple[int, int]
    _climate            : CLIMATE

    def __init__(self, pos:tuple[int, int], clm:CLIMATE):
        self._pos = pos
        self._climate = clm

class Water(Cell):
    _salt           : bool

    def __init__(self, pos: tuple[int, int], salt:bool=False):
        super().__init__(pos)
        self._salt = salt

class Land(Cell):
    def __init__(self, pos: tuple[int, int]):
        super().__init__(pos)

class Map:

    __config            : Config
    __map_config        : MapConfig
    __settings          : Settings

    __grid              : list[list[Cell]]
    __size              : tuple[int, int]

    __label             : Label
    __dsp               : Display

    def update(self):

        pass

    def set(self, cell:Cell, x:int, y:int):
        self.__grid[y][x] = cell

    def get(self, x:int, y:int):
        return self.__grid[y][x]

    def __ud_info(self, txt:str):
            print(txt)
            self.__info.set_text(txt)
            self.__info.update()
            self.__dsp.render()

    def __get_climate(self, y:int) -> CLIMATE:
        diff = abs(y - (self.__map_config.map_size.value[1]/2))
        prc = diff / (self.__map_config.map_size.value[1]/2)
        
        if prc > 0.90: type = CLIMATE.POLAR
        elif prc > 0.65: type = CLIMATE.TEMPERATE
        elif prc > 0.45: type = CLIMATE.DRY
        else: type = CLIMATE.TROPICAL

        self.__ud_info(f'Y: {y:3} | {prc:.5} | {type.name}')
        
        return type

    def __seed_continents(self):
        self.__ud_info('Seeding Continents...')

    def __create_oceans(self, ww, wh, sw, sh):
        self.__ud_info('>> Generating Ocean...')
        cvc = self.__dsp.get_canvas()

        for y in range(wh):
            rect = pygame.Rect(0, y*sh, ww*sw, sh)
            b = 255*(abs(y-wh/2))/(wh/2)
            pygame.draw.rect(cvc, (0, 0, b), rect)
            clm = self.__get_climate(y)
            rect = pygame.Rect(0, y*sh, 2*clm.value, sh)
            pygame.draw.rect(cvc, (255*(clm.value/4.0), 0, 0), rect)
            for x in range(ww):
                rect.topleft = (x*sw, y*sh)
                c = Cell((x, y), clm)
                self.set(c, x, y)

    def __generate(self):
        self.__dsp.clear()
        self.__dsp.render()
        sw, sh = self.__config.win_dim
        ww = self.__map_config.map_size.value[0]
        wh = self.__map_config.map_size.value[1]
        sw /= float(ww)
        sh /= float(wh)
        self.__ud_info(f'Generate {ww}x{wh} nrmlzd {sw:.3}x{sh:.3}')
        self.__ud_info('>> Generating...')
        self.__grid = [[None]*self.__size[0] for _ in range(self.__size[1])]
        self.__create_oceans(ww, wh, sw, sh)
        self.__seed_continents()
        self.__ud_info('>> Done.')

    def __init__(self, cfg:MapConfig, stt:Settings) -> None:
        self.__map_config = cfg
        self.__settings = stt
        self.__config = get_config()
        self.__size = self.__map_config.map_size.value
        self.__info = Label(fg=Color.ORANGE, pos_y=20, pos_x=250, width=500, border_width=0, bg=Color.RED)
        self.__dsp = get_display()
        self.__generate()

