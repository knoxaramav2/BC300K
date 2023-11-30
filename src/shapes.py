

import math
from map import NGon, Vertex

def ngon(center:tuple[float, float], 
         radius:float, verts:int, sdeg:float=0) -> list[Vertex]:

    vertices = []
    deg = sdeg
    d_deg = 360.0/verts
    e_deg = 360.0+sdeg-d_deg
    i = 0
    while i < verts:
        rad = math.radians(d_deg*i)
        x = radius * math.cos(rad) + center[0]
        y = radius * math.sin(rad) + center[1]
        v = Vertex(x, y)
        vertices.append(v)
        i += 1

    return vertices

def hexagon(center:tuple[float, float], rad:float):
    return NGon(ngon(center, rad, 6))

