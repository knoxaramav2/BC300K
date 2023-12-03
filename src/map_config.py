
from enum import Enum


class MapSize(Enum):


    DEV   = (2, 2)
    MICRO = (16, 9)
    TINY  = (20, 18)
    SMALL = (32, 15)
    NORMAL = (100, 44)
    LARGE = (200, 88)
    XLARGE = (512, 288)

class MapConfig:

    auto_gen            : bool = False
    name                : str = ''
    map_name            : str = ''#Can be empty if auto_gen true

    map_size            : MapSize = MapSize.TINY

    temp                : float = 0.30

    def __init__(self):
        pass

__inst__: MapConfig = None
def get_map_config():
    global __inst__
    if __inst__ == None:
        __inst__ = MapConfig()
    return __inst__