
from enum import Enum


class MapSize(Enum):


    MICRO = (16, 9)
    TINY  = (32, 18)
    SMALL = (64, 36)
    NORMAL = (128, 72)
    LARGE = (256, 144)
    XLARGE = (512, 288)

class MapConfig:

    auto_gen            : bool = False
    name                : str = ''
    map_name            : str = ''#Can be empty if auto_gen true

    map_size            : MapSize = MapSize.TINY

    temp                : float = 0.30

    def __init__(self):
        pass