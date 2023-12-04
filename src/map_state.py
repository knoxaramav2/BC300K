

import math
from map import CLIMATE, NGon, Water
from settings import Settings, get_settings

class MapCellState:

    _cell               : NGon
    _population         : int
    _growth_rate        : float
    _food               : float
    _water              : float
    _severity           : float
    _area               : float

    def __calc_growth_rate(self):

        self._growth_rate = (
            self._food+self._water-self._severity
        ) / math.sqrt((self._area**2)+(self._population**2))

    def update(self):
        self.__calc_growth_rate()
        self._population *= self._growth_rate

    def __s_score(self, cell:NGon):
        s_score = 0.0

        match self._cell.content._climate:
            case CLIMATE.DRY: w_score = 1.1
            case CLIMATE.TEMPERATE: w_score = 0.8
            case CLIMATE.POLAR: w_score = 2.0
            case CLIMATE.TROPICAL: w_score = 1.3

        return s_score

    def __f_score(self, cell:NGon):
        f_score = 0.0

        match self._cell.content._climate:
            case CLIMATE.DRY: w_score = 0.8
            case CLIMATE.TEMPERATE: w_score = 1.5
            case CLIMATE.POLAR: w_score = 0.1
            case CLIMATE.TROPICAL: w_score = 1.8

        return f_score

    def __w_score(self, cell:NGon):
        w_score = 0.0
        
        if isinstance(cell.content, Water) and cell.content._salt:
            return 0.0

        match self._cell.content._climate:
            case CLIMATE.DRY: w_score = 0.6
            case CLIMATE.TEMPERATE: w_score = 1.3
            case CLIMATE.POLAR: w_score = 0.4
            case CLIMATE.TROPICAL: w_score = 1.5
        return w_score

    def __calc_water(self):
        w_score = self.__w_score(self._cell)
        for n in self._cell.neighbors:
            if n == None: continue
            w_score += self.__w_score(n)/12
        self._water = w_score

    def __calc_food(self):
        f_score = self.__f_score(self._cell)
        for n in self._cell.neighbors:
            if n == None: continue
            f_score += self.__f_score(n)/12
        self._food = f_score

    def __calc_severity(self):
        s_score = self.__s_score(self._cell)
        for n in self._cell.neighbors:
            if n == None: continue
            s_score += self.__s_score(n)/12
        self._severity = s_score

    def __calc_area(self):

        shape = self._cell
        #Todo calc shape

        self._area = 1.0

    def __init__(self, cell:NGon):
        self._cell = cell
        self._population = 0
        self._growth_rate = 1.0
        self.__calc_water()
        self.__calc_food()
        self.__calc_severity()
        self.__calc_area()
        self.__calc_growth_rate()

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
        else: self._curr_cell = None

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

    def init_cell(self, cell:NGon):
        ms = MapCellState(cell)
        self.__cells.append(ms)
        self._curr_cell = ms

        ms._population = 300

    def __init__(self) -> None:
        self.__cells = []
        self.__settings = get_settings()
        self.__cntr_wrap = self.__settings.update_delay
        self.__counter = self.__cntr_wrap
        self.year = self.__settings.start_year
        self._curr_cell = None
        self.population = 0
        self.avg_tmp = 40.0

