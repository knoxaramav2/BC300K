from __future__ import annotations
from enum import Enum
from tkinter import Canvas

import math
import pygame
from pygame import Rect, Surface

from colors import Color
from display import Display, get_display
from interface import Renderable
from map_config import MapConfig
from settings import Settings, get_settings


CLIMATE = Enum('climate',[
    'POLAR' ,'TEMPERATE' ,'DRY' ,'TROPICAL'
])

class Vertex:
    pos         : tuple[float, float]
    def __init__(self, x:float, y:float) -> None:
        self.pos = (x, y)

class NGon(Renderable):

    box             : tuple[float, float, float, float]
    vertices        : list[Vertex]
    center          : tuple[float, float]
    neighbors       : list[NGon]
    content         : Cella
    DEF_FUZZ        : int = 3.0

    __dsp           : Display
    __cvc           : Canvas

    def local_sibling_vertex(self, trg:Vertex):
        for v in self.vertices:
            if self.compare_vertex(trg, v):
                return v
        return None

    def compare_vertex(self, v1:Vertex, v2:Vertex, fuzz:float=DEF_FUZZ) -> bool:
        d1 = abs(v1.pos[0]-v2.pos[0])
        d2 = abs(v1.pos[1]-v2.pos[1])
        #print(f'{d1<fuzz}, {d2<fuzz} | ({d1:.3}, {d2:.3}) | {v1.pos[0]:.3},{v1.pos[1]:.3} | {v2.pos[0]:.3}, {v2.pos[1]:.3}')
        r1 = abs(v1.pos[0]-v2.pos[0]) <= fuzz
        r2 = abs(v1.pos[1]-v2.pos[1]) <= fuzz
        r3 = abs(v1.pos[0]-v2.pos[0]) <= fuzz and abs(v1.pos[1]-v2.pos[1]) <= fuzz
        return abs(v1.pos[0]-v2.pos[0]) <= fuzz and abs(v1.pos[1]-v2.pos[1]) <= fuzz

    def compare_edge(self, e1:tuple[Vertex, Vertex], e2:tuple[Vertex, Vertex], fuzz:float=DEF_FUZZ) -> bool:   
        return (self.compare_vertex(e1[0], e2[1], fuzz) and self.compare_vertex(e1[1], e2[0], fuzz) or
            self.compare_vertex(e1[0], e2[0], fuzz) and self.compare_vertex(e1[1], e2[1], fuzz))

    def match_edges(self, trg:NGon, fuzz:float=DEF_FUZZ) -> list[tuple[tuple[Vertex, Vertex], tuple[Vertex, Vertex]]]:
        
        len_1 = len(self.vertices)
        len_2 = len(trg.vertices)
        edges = []

        idx_1 = 0
        while idx_1 < len_1:
            e1 = self.get_edge(idx_1)
            idx_2 = 0
            while idx_2 < len_2:
                e2 = trg.get_edge(idx_2)
                if self.compare_edge(e1, e2):
                    edges.append((e1, e2))
                idx_2 += 1
            idx_1 += 1

        return edges

    def get_neighbor(self, idx:int):
        
        if idx < 0: idx = len(self.neighbors) -1 
        elif idx >= len(self.neighbors): idx = 0

        return self.neighbors[idx]

    def get_edge(self, idx:int=0) -> tuple[Vertex, Vertex]:
        length = len(self.vertices)

        if idx >= length: 
            return None
        
        v1 = self.vertices[idx]
        v2 = self.vertices[0] if idx+1 == length else self.vertices[idx+1]

        return (v1, v2)

    def edge_index(self, edge:tuple[Vertex, Vertex]) -> int:
        idx = 0
        while idx < len(self.vertices):
            e = self.get_edge(idx)
            if self.compare_edge(edge, e): 
                return idx
            idx += 1
        return -1

    def vertex_index(self, vert:Vertex):
        i = 0
        while i < len(self.vertices):
            if self.vertices[i] == vert: 
                return i
            i += 1
        return -1

    def add_neighbor(self, shape:NGon, fuzz:float=DEF_FUZZ):
        edges = self.match_edges(shape, fuzz)
        for edge in edges:
            e1_idx = self.edge_index(edge[0])
            e2_idx = shape.edge_index(edge[1])
            v1_idx = self.vertex_index(edge[0][0])
            v2_idx = self.vertex_index(edge[0][1])
            self.neighbors[e1_idx] = shape
            shape.neighbors[e2_idx] = self

            #Marry vertices
            tv1 = shape.local_sibling_vertex(edge[0][0])
            tv2 = shape.local_sibling_vertex(edge[0][1])
            self.vertices[v1_idx] = tv1
            self.vertices[v2_idx] = tv2

    def add_neighbor_edge(self, nghbr:NGon, n_idx:int, src_idx:int):
        ns = nghbr.get_edge(n_idx)
        
        src_e = self.get_edge(src_idx)
        vi1 = self.vertex_index(src_e[0])
        vi2 = self.vertex_index(src_e[1])
        ni1 = nghbr.vertex_index(ns[0])
        ni2 = nghbr.vertex_index(ns[1])

        self.vertices[vi1] = nghbr.vertices[ni2]
        self.vertices[vi2] = nghbr.vertices[ni1]

        self.neighbors[src_idx] = nghbr
        nghbr.neighbors[n_idx] = self

        #print(f'CONN: {src_idx} => {n_idx}')

    def render(self, cvc:Surface, pos:tuple[float, float]=None, zoom:float=1.0, 
               b_clr:Color=Color.GREY, f_clr:Color=Color.LIGHT_GRAY, auto_clr:bool=False):
        if self.content != None and auto_clr:
            if isinstance(self.content, Water) and f_clr == None:
                f_clr = Color.BLUE if self.content._salt else Color.CYAN
            elif isinstance(self.content, Land) and f_clr == None:
                match self.content._climate:
                    case CLIMATE.DRY: f_clr = Color.ORANGE
                    case CLIMATE.TROPICAL: f_clr = Color.GREEN
                    case CLIMATE.TEMPERATE: f_clr = Color.BROWN
                    case _: f_clr = Color.WHITE
        self.draw(cvc, f_clr, b_clr)

    def draw(self, cvc, fill_clr:Color=Color.LIGHT_GRAY, border_clr:Color=Color.GREY):
        coords = [v.pos for v in self.vertices]
        if fill_clr != None and fill_clr != Color.CLEAR:
            pygame.draw.polygon(cvc, fill_clr.value, coords)
        if border_clr != None and border_clr != Color.CLEAR:
            pygame.draw.lines(cvc, border_clr.value, True, coords)

    def calc_geom(self):
        x = 0
        y = 0
        min_x = self.vertices[0].pos[0]
        min_y = self.vertices[0].pos[1]
        max_x = min_x
        max_y = min_y
        for v in self.vertices:
            x += v.pos[0]
            y += v.pos[1]
            min_x = min(min_x, v.pos[0])
            min_y = min(min_y, v.pos[1])
            max_x = max(max_x, v.pos[0])
            max_y = max(max_y, v.pos[1])
        self.box = (min_x, min_y, max_x, max_y)

        
        self.center = (x/len(self.vertices), y/len(self.vertices))

    def in_box(self, x:float, y:float):
        b = self.box
        return ((x >= b[0] and x <= b[2]) and (y >= b[1] and y <= b[3]))

    def __intersection(self, e1, e2) -> Vertex:
        p1 = sorted(e1, key=lambda c:c[0])
        p2 = sorted(e2, key=lambda c:c[0])
        
        y1 = sorted(e1, key=lambda c:c[1])
        y2 = sorted(e2, key=lambda c:c[1])
        
        t1 = (p1[1][1]-p1[0][1])/(p1[1][0]-p1[0][0])
        c1 = p1[0][1]-p1[0][0]*t1
        
        t2 = (p2[1][1]-p2[0][1])/(p2[1][0]-p2[0][0])
        c2 = p2[0][1]-p2[0][0]*t2
                
        if t1 == t2: return None
        x = (c2 - c1)/(t1-t2)
        yi = x*t2+c2
        
        bc = (
            (x >= p1[0][0] and x <= p1[1][0] and yi >= y1[0][1] and yi <= y1[1][1]) and
            (x >= p2[0][0] and x <= p2[1][0] and yi >= y2[0][1] and yi <= y2[1][1])
        )

        return (x, yi) if bc else None

    def in_border(self, x:float, y:float):
        
        if not self.in_box(x, y):
            return False

        b = self.box
        t_e = ((x, y), (b[2]+100, y))

        intrs = 0
        for i in range(len(self.vertices)):
            e = self.get_edge(i)
            p1, p2 = e[0].pos, e[1].pos
            intr = self.__intersection(t_e, (p1, p2))
            if intr != None:
                intrs += 1

        print(f'{x}, {y} | BNDS: {intrs}')
        return intrs%2 == 1

    def __init__(self, vertices:list[Vertex]):
        self.vertices = vertices
        self.neighbors = [None]*len(vertices)
        self.content = None
        self.__dsp = get_display()
        self.__cvc = self.__dsp.get_canvas()
        self.calc_geom()

class Cell:

    _climate            : CLIMATE

    def __init__(self, clm:CLIMATE = None):
        self._climate = clm

class Water(Cell):
    _salt           : bool

    def __init__(self, clm:CLIMATE, salt:bool=False):
        super().__init__(clm)
        self._salt = salt

class Land(Cell):
    def __init__(self, clm:CLIMATE):
        super().__init__(clm)

class Map(Renderable):

    __size          : tuple[int, int]
    __grid          : list[list[NGon]]
    __dsp           : Display
    __cvc           : pygame.Surface
    __stt           : Settings

    def __cell_coord(self, cell:NGon):
        for y in range(len(self.__grid)):
            for x in range(len(self.__grid[y])):
                if cell == self.__grid[y][x]:
                    return x, y
        return -1, -1

    def select_at(self, x:float, y:float) -> NGon:
        for r in self.__grid:
            for c in r:
                if c.in_border(x, y):
                #if c.in_box(x, y):
                    _x, _y = self.__cell_coord(c)
                    print(f'Select @ {_x}, {_y}')
                    return c

    def select_fuzzed(self, fx:float, fy:float, fuzz:float=5.0) -> Vertex:
        #TODO radiating approach
        for y in self.__grid:
            for x in y:
                if x == None: continue
                for v in x.vertices:
                    dx = abs(v.pos[0] - fx)
                    dy = abs(v.pos[1] - fy)
                    if dx < fuzz and dy < fuzz: 
                        return v
        return None

    def render(self, 
               cvc: Surface, 
               pos: tuple[float, float] = None, 
               zoom: float = 1.0,
               auto_clr:bool=True):
        b_clr = Color.CLEAR if not self.__stt.draw_outline else Color.CYAN
        self.draw(auto_clr=auto_clr, f_clr=None, b_clr=b_clr)

    def draw(self, b_clr:Color=Color.CYAN, f_clr:Color=None, auto_clr:bool=False):
        for y in self.__grid:
            for x in y:
                if x == None: break
                x.render(self.__cvc, b_clr=b_clr, f_clr=f_clr,auto_clr=auto_clr)
                #x.draw(self.__cvc, None, Color.CYAN)

    def set(self, cell:NGon, x:int, y:int):
        self.__grid[y][x] = cell

    def get(self, x:int, y:int) -> NGon:
        if x < 0 or y < 0 or x >= self.__size[0] or y >= self.__size[1]: return None
        return self.__grid[y][x]

    def size(self):
        return self.__size

    def __init_grid(self):
        self.__grid = [[None]*(self.__size[0]) for _ in range(self.__size[1])]

    def __init__(self, map_cfg:MapConfig):
        self.__size = map_cfg.map_size.value
        self.__dsp = get_display()
        self.__stt = get_settings()
        self.__cvc = self.__dsp.get_canvas()
        self.__init_grid()
