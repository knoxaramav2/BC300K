
import pygame
from pygame import Surface
from colors import Color

from config import Config, get_config


class Display:

    __clock         : pygame.time.Clock
    __canvas        : Surface
    __screen_dim    : tuple[int, int]

    __cfg           : Config

    def get_canvas(self):
        return self.__canvas

    def render(self):
        pygame.display.update()

    def clear(self, clr:Color=Color.BLACK):
        self.__canvas.fill(clr.value)

    def screen_dim(self) -> tuple[int, int]:
        return self.__screen_dim

    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption('BC 300K')
        w = pygame.display.Info().current_w
        h = pygame.display.Info().current_h
        self.__screen_dim = (w, h)
        self.__cfg = get_config()
        t_dim = self.__cfg.win_dim
        self.__canvas = pygame.display.set_mode((t_dim[0], t_dim[1]))
        self.__clock = pygame.time.Clock()


__inst__: Display = None

def get_canvas():
    global __inst__
    return __inst__.get_canvas()

def get_display():
    global __inst__
    if __inst__ == None:
        __inst__ = Display()
    return __inst__