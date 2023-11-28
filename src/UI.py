
from pygame import Rect

from display import Display, get_display


class Control:

    _bounds         : Rect
    _display        : Display

    def update(self):
        self._display.clear()

    def move(self, x:int, y:int):
        self._bounds.topleft = (x, y)

    def __init__(self):
        self._bounds = Rect(0, 0, 0, 0)
        self._display = get_display()

        