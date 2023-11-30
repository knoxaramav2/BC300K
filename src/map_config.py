
from enum import Enum


class MapSize(Enum):


    MICRO = (16, 9)
    TINY  = (160, 90)
    SMALL = (320, 180)
    NORMAL = (640, 360)
    LARGE = (960, 540)
    XLARGE = (1280, 720)

class MapConfig:

    auto_gen            : bool = False
    name                : str = ''
    map_name            : str = ''#Can be empty if auto_gen true

    map_size            : MapSize = MapSize.MICRO

    temp                : float = 0.30

    def __init__(self):
        pass