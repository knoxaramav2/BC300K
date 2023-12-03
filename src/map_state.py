

from map import NGon
from settings import Settings, get_settings


class MapCellState:

    _cell           : NGon
    _population     : int

    def update(self):
        pass

    def __init__(self, cell:NGon):
        self._cell = cell
        self._population = 0

class MapState:

    year            : int
    population      : int
    avg_tmp         : float

    __cells         : list[MapCellState]
    __counter       : int
    __cntr_wrap     : int

    __settings      : Settings
    
    _curr_cell      : MapCellState

    def set_cell(self, cell:NGon):
        c = [t for t in self.__cells if t._cell]
        if len(c) > 0: self._curr_cell = c[0]

    def add_cell(self,  new:NGon, origin:MapCellState=None):
        ms = MapCellState(new)
        self.__cells.append(ms)

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

        self.population = 0
        for cell in self.__cells:
            self.population += cell._population
            cell.update()
        
        return True

    def __init__(self) -> None:
        self.__cells = []
        self.__settings = get_settings()
        self.__cntr_wrap = self.__settings.update_delay
        self.__counter = self.__cntr_wrap
        self.year = self.__settings.start_year
        self._curr_cell = None
        self.population = 0
        self.avg_tmp = 40.0

