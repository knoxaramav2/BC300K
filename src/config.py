import sys

import pygame

class Config:

    win_dim         : tuple[int, int]

    def __parse_cli(self):
        args = sys.argv
        
        for arg in args:
            trms = arg.split('=')
            k = trms[0].lower()
            v = None if len(trms) != 2 else trms[1]

            match k:
                case 'dim':
                    wh = v.split('x')
                    self.win_dim = (int(wh[0]), int(wh[1]))
                case _:
                    pass

    def __init__(self):
        w = pygame.display.Info().current_w/2
        h = pygame.display.Info().current_h/2
        self.win_dim = (w, h)

        self.__parse_cli()


__inst__: Config = None

def get_config():
    global __inst__
    if __inst__ == None:
        __inst__ = Config()
    return __inst__

