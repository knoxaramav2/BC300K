from enum import Enum
import math
from random import randint
import random

import shapely as shp
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import numpy as np
import pygame
from numpy import random
from pygame import Rect
from UI import Label
from colors import Color
from config import Config, get_config
from display import Display, get_display
from map_config import MapConfig, MapSize
from settings import Settings

CLIMATE = Enum('climate',[
    'POLAR' ,'TEMPERATE' ,'DRY' ,'TROPICAL'
])

class Cell:

    _pos                : tuple[int, int]
    _climate            : CLIMATE

    def __init__(self, clm:CLIMATE, pos:tuple[int, int]=(0, 0)):
        self._climate = clm
        self._pos = pos

class Water(Cell):
    _salt           : bool

    def __init__(self, clm:CLIMATE, salt:bool=False):
        super().__init__(clm)
        self._salt = salt

class Land(Cell):
    def __init__(self, clm:CLIMATE):
        super().__init__(clm)

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
        cell._pos = (x, y)
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

    def __climate_clr(self, cc:CLIMATE):
        clr:Color
        if cc == CLIMATE.POLAR: clr = Color.CYAN
        elif cc == CLIMATE.TEMPERATE: clr = Color.BROWN
        elif cc == CLIMATE.TROPICAL: clr = Color.GREEN
        else: clr = Color.RED

        return clr

    def __d_order(self, points:list[Cell]):
        ret = sorted(points, key=lambda c:math.sqrt(math.pow(c._pos[0], 2)+math.pow(c._pos[1] ,2)))
        return ret

    def __draw_cell(self, cvc, x, y, sw, sh, clr:Color):
        pygame.draw.circle(cvc, clr.value, (x*sw+5, y*sh+5), 3, 1)

    def __grow_seeds(self, ww, wh, sw, sh, seeds:[Cell]):
        size = self.__map_config.map_size.value
        cvc = self.__dsp.get_canvas()
        rng = np.random
        
        #Tuning
        DEG_FRAC = 50.0
        MV_VAR = 0.01
        DD_MIN = 0.85
        DD_MAX = 1.15

        mjr_deg = 360.0/((ww / MapSize.SMALL.value[0])*DEG_FRAC)
        mnr_deg = mjr_deg/10.0

        mjr_arr = []
        mnr_arr = []

        ln = len(seeds)
        idx = 0
        retry = False
        retries = 0
        while idx < ln:
            if retry:
                retry = False
                retries += 1
                print('>> Retry')

                if retries > 50:
                    print('ERR: Impossible island calculation')
                    exit(-1)

            seed = seeds[idx]
            self.__draw_cell(cvc, seed._pos[0], seed._pos[1], sw, sh, Color.YELLOW)

            last_pos = None
            arr = []
            c_clr = random.choice(list(Color))
            s_pos = (seed._pos[0], seed._pos[1])
            
            em_x = rng.uniform(-MV_VAR, MV_VAR)
            eM_x = rng.uniform(-MV_VAR, MV_VAR)
            em_y = rng.uniform(-MV_VAR, MV_VAR)
            eM_y = rng.uniform(-MV_VAR, MV_VAR)

            em_x, eM_x = sorted([em_x, eM_x])
            em_y, eM_y = sorted([em_y, eM_y])
            
            for deg in range(0, 360, int(mjr_deg)):
                pygame.event.clear()
                
                fails = 0
                while True:
                    s_pos = (s_pos[0]+rng.uniform(em_x, eM_x), 
                             s_pos[1]+rng.uniform(em_y, eM_y))
                    self.__draw_cell(cvc, s_pos[0], s_pos[1], sw, sh, random.choice(list(Color)))

                    collide = False
                    for mr in mjr_arr:
                        p_arr = [p._pos for p in mr]
                        collide = self.__in_bounds(p_arr, s_pos)
                    if not collide: 
                        break

                    fails += 1
                    if fails > 100:
                        print('Failed to move island')
                        break

                while True:
                    rad = math.radians(deg)
                    d = 30*sw*rng.uniform(DD_MIN, DD_MAX)

                    x = (math.cos(rad) * d) + s_pos[0]
                    y = (math.sin(rad) * d) + s_pos[1]

                    x = max(min(x, ww-1), 0)
                    y = max(min(y, wh-1), 0)

                    px = int(x)
                    py = int(y)

                    collide = False
                    for mr in mjr_arr:
                        p_arr = [p._pos for p in mr]
                        collide = self.__in_bounds(p_arr, (px, py))
                    if not collide: break
                    
                    fails += 1
                    if fails > 100:
                        print('Cannot find point')
                        break                

                lnd = Land(self.__get_climate(py))
                self.set(lnd, px, py)
                arr.append(lnd)

                self.__draw_cell(cvc, lnd._pos[0], lnd._pos[1], sw, sh, Color.ORANGE)
                if last_pos != None:
                    pygame.draw.line(cvc, c_clr.value, 
                                     (last_pos[0]*sw,last_pos[1]*sh), 
                                     (lnd._pos[0]*sw,lnd._pos[1]*sh),
                                     width=2)
                last_pos = lnd._pos
                self.__ud_info(f'Shore: {rad:.3}, {px}, {py}')
                       
            pygame.draw.line(cvc, c_clr.value, 
                             (last_pos[0]*sw, last_pos[1]*sh), 
                             (arr[0]._pos[0]*sw, arr[0]._pos[1]*sh), 
                             width=2)
            mjr_arr.append(arr)
            coords = [(c._pos[0]*sw, c._pos[1]*sh) for c in mjr_arr[-1]]
            pygame.draw.polygon(cvc, c_clr.value, coords)
            self.__ud_info('Drew major shore')
            idx += 1

    def __in_bounds(self, coords, point):
        pnt = Point(point[0], point[1])
        poly = Polygon([c for c in coords])
        return poly.contains(pnt)

    def __seed_continents(self, ww, wh, sw, sh) -> [Cell]:
        self.__ud_info('Seeding Continents...')

        num_seeds = ((self.__map_config.map_size.value[0])/MapSize.SMALL.value[0]) * 3
        seeds = []
        cvc = self.__dsp.get_canvas()

        MIN_DIST = 0.15 * math.sqrt(math.pow(ww,2)+math.pow(wh,2))
        
        for n in range(int(num_seeds)):
            
            #Attempt to seed at least 10% away from other islands
            for atmpt in range(0, 10):
                rx = int(random.uniform(ww*.05, ww*.95))
                ry = int(random.uniform(wh*.05, wh*.95))
                m_dst = 99999
                for seed in seeds:
                    m_dst = min(m_dst,
                        math.dist([rx, ry], [seed._pos[0], seed._pos[1]]))
                if m_dst > MIN_DIST:
                    break

            r = Rect(rx*sw, ry*sh, 10*sw, 10*sh)
            r.center = r.topleft
            cc = self.__get_climate(ry)
            clr = self.__climate_clr(cc)
            c = Land(cc)
            self.set(c, rx, ry)
            seeds.append(c)
            self.__draw_cell(cvc, rx, ry, sw, sh, clr)
            self.__ud_info(f'SEED {rx}, {ry} ({cc.name})')

        return self.__d_order(seeds)

    def __create_oceans(self, ww, wh, sw, sh):
        self.__ud_info('>> Generating Ocean...')
        cvc = self.__dsp.get_canvas()

        for y in range(wh):
            rect = Rect(0, y*sh, ww*sw, sh)
            b = 255*(abs(y-wh/2))/(wh/2)
            pygame.draw.rect(cvc, (0, 0, b), rect)
            clm = self.__get_climate(y)
            rect = Rect(0, y*sh, 2*clm.value, sh)
            pygame.draw.rect(cvc, (255*(clm.value/4.0), 0, 0), rect)
            for x in range(ww):
                rect.topleft = (x*sw, y*sh)
                c = Water((x, y), clm)
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
        seeds = self.__seed_continents(ww, wh, sw, sh)
        self.__grow_seeds(ww, wh, sw ,sh, seeds)
        self.__ud_info('>> Done.')

    def __init__(self, cfg:MapConfig, stt:Settings) -> None:
        self.__map_config = cfg
        self.__settings = stt
        self.__config = get_config()
        self.__size = self.__map_config.map_size.value
        self.__info = Label(fg=Color.ORANGE, pos_y=20, pos_x=250, width=500, border_width=0, bg=Color.RED)
        self.__dsp = get_display()
        while True:
            pygame.event.clear()
            self.__generate()

