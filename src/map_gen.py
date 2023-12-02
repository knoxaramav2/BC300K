
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
from map import CLIMATE, Cell, Land, Map, NGon, Vertex, Water
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

    PERT_RAND       : float = 1.1
    PERT_MAG        : float = 0.09
    PERT_COEF       : float = 0.95
    PERT_CUTTOFF    : float = 0.01

    OCEAN_RAND      : float = 1.1
    OCEAN_MAG       : float = 0.09
    OCEAN_COEF      : float = 0.95
    OCEAN_CUTTOFF   : float = 0.01

    LAND_RAND       : float = 1.1
    LAND_MAG        : float = 0.50
    LAND_COEF       : float = 0.95
    LAND_CUTOFF     : float = 0.01

    def __prnt(self, txt:str):
        print(txt)
        self.__info.set_text(txt)
        self.__info.update()
        self.__dsp.render()

    def __get_climate(self, lat:int) -> CLIMATE:
        m_y = self.__map.size()[1]
        r = abs(float(lat)/float(m_y)-0.5)
        if r < 0.10: return CLIMATE.DRY
        if r < 0.25: return CLIMATE.TROPICAL
        if r < 0.35: return CLIMATE.TEMPERATE
        return CLIMATE.POLAR

    def __grow_land(self, x:int, y:int, amnt:float):
        cell = self.__map.get(x, y)
        if cell == None or amnt < self.LAND_CUTOFF: 
            return
        clm = self.__get_climate(y)
        lnd = Land(clm)
        cell.content = lnd
        cell.render(self.__cvc, auto_clr=True)
        self.__prnt(f'LAND: {clm.name}')

        for xx in range(x-1, x+1):
            for yy in range(y-1, y+1):
                n = self.__map.get(xx, yy)
                if n == None: 
                    continue
                if isinstance(n.content, Land):
                    continue
                r_val = amnt*self.LAND_COEF * abs(np.random.normal(scale=0.45, loc=0))
                self.__grow_land(xx, yy, r_val)

    def __spawn_land(self):

        sz = self.__map.size()
        rt = int(math.sqrt(sz[0]**2+sz[1]**2))

        for i in range(rt):
            x = int(np.random.uniform(0, sz[0]))
            y = int(np.random.uniform(0, sz[1]))
            self.__grow_land(x, y, self.LAND_MAG)

    def __spawn_ocean(self):
        map = self.__map
        size = self.__map.size()
        for y in range(size[1]):
            for x in range(size[0]):
                cell = map.get(x, y)
                clm = self.__get_climate(y)
                oc = Water(clm, True)
                cell.content = oc
                cell.render(self.__cvc, auto_clr=True)
            prc = y/size[1]
            self.__prnt(f'GEN OCEANS: CLIMATE - {clm.name} @ %{prc} ')

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
        if cell == None or amnt < self.PERT_CUTTOFF: return
        pygame.event.clear()
        self.__dsp.clear()
        self.__map.draw()
        #self.__prnt(f'PERTURB: {cell.center[0]:.2}, {cell.center[1]:.2} : {amnt}')

        for i in range(len(cell.vertices)):
            v = cell.vertices[i]
            if self.__is_edge_vert(i, x, y): continue
            n1 = cell.get_neighbor(i+1)
            n2 = cell.get_neighbor(i-1)
            pnts = [cell.center]
            if n1 != None: pnts.append(n1.center)
            if n2 != None: pnts.append(n2.center)
            box = self.__min_box(pnts)
            dx = np.random.uniform(box[0]-cell.center[0], box[1]-cell.center[0])*amnt*np.random.normal(scale=self.PERT_RAND)
            dy = np.random.uniform(box[2]-cell.center[1], box[3]-cell.center[1])*amnt*np.random.normal(scale=self.PERT_RAND)
            v.pos = (v.pos[0] + dx, v.pos[1] + dy)

            self.__map.draw()

            for cy in range(-1, 1):
                for cx in range(-1, 1):
                    if cy == 0 and cx == 0: continue
                    self.__perturb_cell(cx, cy, amnt*self.PERT_COEF)

    def __perturb(self, map:Map):

        m_cycles = self.__map_cfg.map_size.value[0] * self.__map_cfg.map_size.value[1]

        rng = random
        for i in range(m_cycles*2):
            x = int(rng.uniform(0, map.size()[0]-1))
            y = int(rng.uniform(0, map.size()[1]-1))

            self.__perturb_cell(x, y, self.PERT_MAG)
            #map.draw()
            map.render(self.__cvc)
            pygame.event.clear()
            self.__prnt(f'CYCLE: {i}')

    def warp_gen(self) -> Map:
        self.__dsp.clear()
        self.__prnt('<<<WARP GEN>>>')
        self.__dsp.clear()
        map = self.__create_pent_map()
        self.__map = map
        self.__perturb(map)
        self.__spawn_ocean()
        self.__spawn_land()
        self.__prnt('<<<DONE>>>')
        return map

    def __init__(self, map_config:MapConfig, stt:Settings):
        self.__info = Label(fg=Color.ORANGE, pos_y=20, pos_x=250, width=500, border_width=0, bg=Color.RED)
        self.__map_cfg = map_config
        self.__cfg = get_config()
        self.__settigns = stt  
        self.__dsp = get_display()
        self.__cvc = self.__dsp.get_canvas()