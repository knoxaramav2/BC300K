from enum import Enum
from display import get_display
from map_config import MapConfig
from settings import Settings

CLIMATE = Enum('climate',[
    
])

class Cell:

    _pos                : tuple[int, int]

    def __init__(self) -> None:
        pass

class Map:

    __config            : MapConfig
    __settings          : Settings

    __grid              : list[list[Cell]]
    __size              : tuple[int, int]

    def update(self):

        pass

    def set(self, cell:Cell, x:int, y:int):
        self.__grid[y][x] = cell

    def get(self, x:int, y:int):
        return self.__grid[y][x]

    def __generate(self):
        dsp = get_display()
        dsp.clear()
        dsp.render()
        
        print('>> Generating...')
        [[None]*self.__size[0] for _ in range(self.__size[1])]
        print('>> Done.')

    def __init__(self, cfg:MapConfig, stt:Settings) -> None:
        self.__config = cfg
        self.__settings = stt
        self.__size = self.__config.map_size.value

        self.__generate()

