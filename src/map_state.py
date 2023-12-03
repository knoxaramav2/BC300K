

from map import NGon
from settings import Settings, get_settings


class MapCellState:

    __cell          : NGon

    def update(self):
        pass

    def __init__(self, cell:NGon):
        self.__cell = cell

class MapState:

    year            : int

    __cells         : list[MapCellState]
    __counter       : int
    __cntr_wrap     : int

    __settings      : Settings

    def add_cell(self,  new:NGon, origin:MapCellState=None):
        ms = MapCellState(new)
        self.__cells.append(ms)
    
    def __gauss(self, x, mu, sig):

        pass

    def update(self) -> bool:
        self.__counter += 1
        if self.__counter >= self.__cntr_wrap:
            self.__counter = 0
        else: return False
        
        #control year rate
        if self.year < -100000: self.year += 1000
        elif self.year < -10000: self.year += 300
        elif self.year < -5000: self.year += 150
        elif self.year < -1000: self.year += 100
        elif self.year < 1500: self.year += 50
        elif self.year < 1900: self.year += 5
        elif self.year < 2000: self.year += 2
        else: self.year += 1

        for cell in self.__cells:
            cell.update()

        return True

    def __init__(self) -> None:
        self.__cells = []
        self.__settings = get_settings()
        self.__cntr_wrap = self.__settings.update_delay
        self.__counter = self.__cntr_wrap
        self.year = self.__settings.start_year

