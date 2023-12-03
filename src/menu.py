
import sys
import pygame
from enum import Enum
from UI import *
from UI import Color, Control
from colors import Color
from config import get_config
from display import Display
from map_config import MapConfig
from map_state import MapState
from settings import Settings
from util import group_fnc


MENU_RESULT = Enum(
    'menu_result', [
        'OK',
        'CANCEL',
        'QUIT',
        'NEW', 'LOAD',
        'SETTINGS'
    ]
)

class Menu (Container):

    _active             : bool
    _ret                : MENU_RESULT
    _focus              : Control 

    def __handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                kn = pygame.key.name(e.key)
                if e.key == pygame.K_ESCAPE:
                    self._active = False
                    self._ret = MENU_RESULT.CANCEL
                elif len(kn) == 1 and kn.isalnum():
                    if isinstance(self._focus, Writeable): self._focus.on_type(pygame.key.name(e.key))
                elif e.key == pygame.K_BACKSPACE:
                    if isinstance(self._focus, Writeable): self._focus.on_backspace()
            elif e.type == pygame.MOUSEBUTTONUP:
                m_pos = pygame.mouse.get_pos()
                for c in self._children:
                    if not c.content._bounds.collidepoint(m_pos[0], m_pos[1]): continue
                    self._focus = c.content

                    if isinstance(c.content, Clickable):c.content.on_click()

    def __loop(self):
        while self._active:
            #self._display.clear()
            self.__handle_events()
            self.update()
            self._display.render()

    def update(self):
        super().update()

    def show(self):
        self._active = True
        self.__loop()
        return self._ret

    def __init__(self, width=0, height=0, 
                 pos_x=0, pos_y=0, 
                 border_width: int = 3, 
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, 
                 border: Color = Color.LIGHT_GRAY, parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent)

        self._active = True
        self._ret = MENU_RESULT.OK
        self._focus = None

        self._bounds.centerx = self._display.get_canvas().get_width()/2
        self._bounds.centery = self._display.get_canvas().get_height()/2
        
class LoadMenu(Menu):

    __map           : MapConfig

    def __init__(self, map:MapConfig):
        self.__map = map

        cfg = get_config()
        width, height = cfg.win_dim
        super().__init__( width=width, height=height, border_width=0)

class NewMenu(Menu):

    __map           : MapConfig
    __settings      : Settings

    __auto_gen      : CheckBox
    __name          : Text

    def __init__(self, map:MapConfig, stt:Settings):
        self.__map = map
        self.__settings = stt

        cfg = get_config()
        width, height = cfg.win_dim
        super().__init__( width=width, height=height, border_width=0)
        
        btn_width = 120

        def fnc(self:NewMenu, res:MENU_RESULT):
            
            if res == MENU_RESULT.NEW:
                self.__name._border_width=0
                if self.__name._value == '':
                    err_label.set_text('ERR: Missing world name')
                    self.__name._border_width=3
                    return

                self.__map.auto_gen = self.__auto_gen._value
                self.__map.map_name = self.__name._value

            self._active = False
            self._ret = res

        err_label = Label(text='', fg=Color.RED, border_width=0, border=Color.RED)
        name_label = Label(text='World Title', border_width=0)
        self.__name = Text(text='Name' ,width=500, border_width=0, border=Color.RED)
        self.__auto_gen = CheckBox(text='Generate', value=map.auto_gen, fg=Color.BLACK)
        cancel = Button(text='Cancel', callback=lambda:fnc(self, MENU_RESULT.CANCEL), width=btn_width, fg=Color.BLACK, border=Color.GREY, bg=Color.LIGHT_GRAY)
        start = Button(text='Start', callback=lambda:fnc(self, MENU_RESULT.NEW), width=btn_width, fg=Color.BLACK, border=Color.GREY, bg=Color.LIGHT_GRAY)

        self.insert(name_label, 0, 0, ALIGN.CENTER)
        self.insert(self.__name, 1, 0, ALIGN.LEFT)
        self.insert(self.__auto_gen, 1, 1, ALIGN.CENTER)
        self.insert(cancel, 0, 2, ALIGN.CENTER)
        self.insert(start, 2, 2, ALIGN.CENTER)

        self.insert(err_label, 1, 4, ALIGN.LEFT)

        self.pack()

class SettingsMenu(Menu):

    _settings       : Settings

    def __init__(self, stt:Settings):
        cfg = get_config()
        width, height = cfg.win_dim
        super().__init__( width=width, height=height, border_width=0)

        btn_width = 120

        def fnc(self:SettingsMenu, res:MENU_RESULT):
            self._active = False
            self._ret = res

            if res == MENU_RESULT.OK:
                pass

        cancel = Button(text='Cancel', callback=lambda:fnc(self, MENU_RESULT.CANCEL), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        accept = Button(text='Accept', callback=lambda:fnc(self, MENU_RESULT.OK), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)

        self.insert(accept, 0, 0, ALIGN.CENTER)
        self.insert(cancel, 1, 0, ALIGN.CENTER)

        self.pack()

class MainMenu(Menu):

    def __init__(self):
        cfg = get_config()
        width, height = cfg.win_dim
        super().__init__( width=width, height=height, border_width=0)

        btn_width = 120

        def fnc(self, res:MENU_RESULT):
            self._active = False
            self._ret = res

        quit = Button(text='QUIT', callback=lambda:fnc(self, MENU_RESULT.QUIT), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        new = Button(text='NEW GAME', callback=lambda:fnc(self, MENU_RESULT.NEW), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        load = Button(text='LOAD GAME', callback=lambda:fnc(self, MENU_RESULT.LOAD), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        settings = Button(text='SETTINGS', callback=lambda:fnc(self, MENU_RESULT.SETTINGS), width=btn_width, border=Color.GREY, bg=Color.LIGHT_GRAY)
        self.insert(new, 0, 0, ALIGN.CENTER)
        self.insert(load, 0, 1, ALIGN.CENTER)
        self.insert(settings, 0, 2, ALIGN.CENTER)
        self.insert(quit, 0, 3, ALIGN.CENTER)

        self.pack()

class StatDisplay(Container):

    __stat          : MapState

    def update(self):
        super().update()
        
        self.population.set_text(f'POP: {self.__stat.population}')
        self.avg_temp.set_text(f'TMP: {self.__stat.avg_tmp:.3}')

    def __init__(self, stat:MapState, width=0, height=0, pos_x=0, pos_y=0, border_width: int = 3, padx: int = 0, pady: int = 0, fg=Color.WHITE, bg=Color.BLACK, border: Color = Color.LIGHT_GRAY, parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent)
        self.__stat = stat
        self.population = Label(text='POP: ', pos_x=100)
        self.avg_temp = Label(text='TMP: ')

        self.insert(self.population, 0, 0, ALIGN.LEFT)
        self.insert(self.avg_temp, 1, 0, ALIGN.LEFT)

        self.pack()

class PauseMenu(Menu):
    def __init__(self, ok_callback:Callable, cancel_callback:Callable, quit_callback:Callable):
        width, height = get_config().win_dim
        width /= 2
        height /= 2
        super().__init__(width, height)
        
        def __close_win():
            self._active = False

        ok_callback = group_fnc(__close_win, ok_callback)
        cancel_callback = group_fnc(__close_win, cancel_callback)
        quit_callback = group_fnc(__close_win, quit_callback)

        title = Label(text='Pause')
        btn_ok = Button(text='OK', callback=ok_callback)
        btn_cancel = Button(text='Cancel', callback=cancel_callback)
        btn_quit = Button(text='Quit', callback=quit_callback)

        self.insert(title, 2, 0, ALIGN.CENTER)
        self.insert(btn_quit, 0, 3, ALIGN.CENTER)
        self.insert(btn_cancel, 3, 3, ALIGN.CENTER)
        self.insert(btn_ok, 4, 3, ALIGN.CENTER)

        self.pack()

