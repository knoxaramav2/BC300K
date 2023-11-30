from __future__ import annotations
from enum import Enum

import pygame

from colors import Color
from display import Display, get_display
from map_config import MapConfig


CLIMATE = Enum('climate',[
    'POLAR' ,'TEMPERATE' ,'DRY' ,'TROPICAL'
])

class Vertex:
    pos         : tuple[float, float]
    def __init__(self, x:float, y:float) -> None:
        self.pos = (x, y)

class NGon:

    vertices        : list[Vertex]
    center          : tuple[float, float]
    neighbors       : list[NGon]
    content         : Cell
    DEF_FUZZ        : int = 1.0

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

            # tv1.pos = (tv1.pos[0], tv1.pos[1]-20) 
            # tv2.pos = (tv2.pos[0], tv2.pos[1]+20) 
            
    def draw(self, cvc, fill_clr:Color=Color.LIGHT_GRAY, border_clr:Color=Color.GREY):
        coords = [v.pos for v in self.vertices]
        if fill_clr != None:
            pygame.draw.polygon(cvc, fill_clr.value, coords)
        if border_clr != None:
            pygame.draw.lines(cvc, border_clr.value, True, coords)

    def __init__(self, vertices:list[Vertex]):
        self.vertices = vertices
        self.neighbors = [None]*len(vertices)

        x = 0
        y = 0
        for v in vertices:
            x += v.pos[0]
            y += v.pos[1]
        
        self.center = (x/len(vertices), y/len(vertices))

class Cell:

    _climate            : CLIMATE

    def __init__(self, clm:CLIMATE = None):
        self._climate = clm

class Water(Cell):
    _salt           : bool

    def __init__(self, cell:Cell, salt:bool=False):
        super().__init__(cell)
        self._salt = salt

class Land(Cell):
    def __init__(self, cell:Cell):
        super().__init__(cell)

class Map:

    __size          : tuple[int, int]
    __grid          : list[list[NGon]]
    __dsp           : Display
    __cvc           : pygame.Surface

    def draw(self):
        for y in self.__grid:
            for x in y:
                if x == None: 
                    break
                x.draw(self.__cvc)

    def set(self, cell:NGon, x:int, y:int):
        self.__grid[y][x] = cell

    def get(self, x:int, y:int) -> NGon:
        return self.__grid[y][x]

    def __init_grid(self):
        self.__grid = [[None]*(self.__size[0]) for _ in range(self.__size[1])]

    def __init__(self, map_cfg:MapConfig):
        self.__size = map_cfg.map_size.value
        self.__dsp = get_display()
        self.__cvc = self.__dsp.get_canvas()
        self.__init_grid()
