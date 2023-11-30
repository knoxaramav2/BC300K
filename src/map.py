from __future__ import annotations
from enum import Enum

import pygame

from colors import Color


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

    def draw(self, cvc, clr:Color=Color.WHITE,
               fill:bool=True, edge:bool=False):
        coords = [v.pos for v in self.vertices]
        if fill:
            pygame.draw.polygon(cvc, clr.value, coords)
        if edge:
            pygame.draw.lines(cvc, clr.value, True, coords)

    def __init__(self, vertices:list[Vertex]):
        self.vertices = vertices
        self.neighbors = []

        x = 0
        y = 0
        for v in vertices:
            x += v.pos[0]
            y += v.pos[1]
        
        self.center = (x/len(vertices), y/len(vertices))

class Cell:

    _pos                : tuple[float, float]
    _climate            : CLIMATE

    def __init__(self, 
                 clm:CLIMATE, 
                 pos:tuple[int, int]=(0, 0)):
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

    def __init__(self) -> None:
        pass
