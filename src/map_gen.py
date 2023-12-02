
import math
import random
import time
import pygame
import numpy as np
from numpy import random
from UI import Label
from colors import Color
from config import Config, get_config
from display import Display, get_display
from map import Cell, Map, NGon, Vertex
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
    __map           : Map

    RANDOM          : float = 1.1
    CHAIN_MAG       : float = 0.09
    CHAIN_COEF      : float = 0.95
    CUTTOFF         : float = 0.01

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
        #m_x = 20
        #m_y = 20

        a_x = math.cos(math.radians(60))
        a_y = math.sin(math.radians(60))
        dx = 0
        dy = (5.0/6.0)*r
        offs = 0

        for y in range(m_y):
            clrb = random.choice(list(Color))
            clrf = random.choice(list(Color))
            print()
            for x in range(m_x):
                cx = (r+(3*r*x))*a_x+((y%2-1)*dx) + offs
                cy = (r+(2*r*y))*a_y+((x%2)*dy)-(2*r) + offs
                
                h=hexagon((cx, cy), r)

                if x%2 == 1:
                    xs_sel = 3
                    xd_sel = 0
                else:
                    xs_sel = 2
                    xd_sel = 5

                if x > 0:
                    h.add_neighbor_edge(map.get(x-1, y), xd_sel, xs_sel)                   
                if y > 0:
                    #Top
                    h.add_neighbor_edge(map.get(x, y-1), 1, 4)
                    if x < m_x - 1 and x%2 == 0:
                        h.add_neighbor_edge(map.get(x+1, y-1), 2, 5)
                if y > 0 and x > 0:
                    h.add_neighbor_edge(map.get(x-1, y), xd_sel, xs_sel)
                    
                map.set(h, x, y)
            h.draw(self.__cvc, None, Color.CYAN)
            self.__prnt(f'| {cx}, {cy} | ({x}, {y})')
            pygame.event.clear()
        self.__dsp.clear()
        map.draw()
        pygame.display.update()
        return map

    def __dist(self, v1:tuple[int, int], v2:tuple[int, int]):
        dx = v1[0] - v2[0]
        dy = v1[1] - v2[1]
        return math.sqrt(dx**2 + dy**2)

    def __point_average(self, points:tuple[float, float]) -> tuple[int, int]:
        
        a_x = 0
        a_y = 0

        for i in range(len(points)):
            a_x += points[i][0]
            a_y += points[i][1]

        a_x /= len(points)
        a_y /= len(points)

        return (a_x, a_y)

    def __is_edge_vert(self, vert_idx:int, cell_x:int, cell_y:int):
        return ((cell_x == 0 and (vert_idx == 1 or vert_idx == 2 or vert_idx == 6)) or
            (cell_x == self.__map.size()[0]-1 and (vert_idx >= 3 and vert_idx <= 5)) or
            (cell_y == 0 and (vert_idx >= 4 and vert_idx <= 6)) or
            (cell_y == self.__map.size()[1]-1 and (vert_idx >= 1 and vert_idx <= 4)))
    
    def __min_box(self, points:list[tuple[int, int]]):
        m_x = 999999
        M_x = -999999
        m_y = 999999
        M_y = -999999

        for v in points:
            m_x = min(m_x, v[0])
            M_x = max(M_x, v[0])
            m_y = min(m_y, v[1])
            M_y = max(M_y, v[1])

        return (m_x, M_x, m_y, M_y)

    def __perturb_cell(self, x:int, y:int, amnt:float):
        cell = self.__map.get(x, y)
        if cell == None or amnt < self.CUTTOFF: return
        pygame.event.clear()
        self.__dsp.clear()
        self.__map.draw()
        self.__prnt(f'PERTURB: {cell.center[0]:.2}, {cell.center[1]:.2} : {amnt}')

        for i in range(len(cell.vertices)):
            v = cell.vertices[i]
            if self.__is_edge_vert(i, x, y): continue
            n1 = cell.get_neighbor(i+1)
            n2 = cell.get_neighbor(i-1)
            pnts = [cell.center]
            if n1 != None: pnts.append(n1.center)
            if n2 != None: pnts.append(n2.center)
            box = self.__min_box(pnts)
            dx = np.random.uniform(box[0]-cell.center[0], box[1]-cell.center[0])*amnt*np.random.normal(scale=self.RANDOM)
            dy = np.random.uniform(box[2]-cell.center[1], box[3]-cell.center[1])*amnt*np.random.normal(scale=self.RANDOM)
            v.pos = (v.pos[0] + dx, v.pos[1] + dy)

            self.__map.draw()

            for cy in range(-1, 1):
                for cx in range(-1, 1):
                    if cy == 0 and cx == 0: continue
                    self.__perturb_cell(cx, cy, amnt*self.CHAIN_COEF)

    def __perturb(self, map:Map):

        m_cycles = self.__map_cfg.map_size.value[0] * self.__map_cfg.map_size.value[1]

        rng = random
        for i in range(m_cycles*2):
            x = int(rng.uniform(0, map.size()[0]-1))
            y = int(rng.uniform(0, map.size()[1]-1))

            self.__perturb_cell(x, y, self.CHAIN_MAG)
            map.draw()
            pygame.event.clear()
            self.__prnt(f'CYCLE: {i}')

    def warp_gen(self) -> Map:
        self.__dsp.clear()
        self.__prnt('<<<WARP GEN>>>')
        self.__dsp.clear()
        map = self.__create_pent_map()
        self.__map = map
        self.__perturb(map)
        self.__prnt('<<<DONE>>>')
        return map

    def __init__(self, map_config:MapConfig, stt:Settings):
        self.__info = Label(fg=Color.ORANGE, pos_y=20, pos_x=250, width=500, border_width=0, bg=Color.RED)
        self.__map_cfg = map_config
        self.__cfg = get_config()
        self.__settigns = stt  
        self.__dsp = get_display()
        self.__cvc = self.__dsp.get_canvas()