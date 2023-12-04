

from enum import Enum
import pygame
from UI import ALIGN, Button, Label
from camera import Camera
from colors import Color
from config import Config, get_config
from display import Display, get_display
from map import Land, Map, NGon, Vertex
from map_config import MapConfig
from map_state import MapState
from menu import Menu, PauseMenu, StatDisplay
from settings import Settings

GAME_STATE = Enum('',[
    'NORMAL',
    'MENU',
    'START_SELECT'
])

EVENT_TYPE = Enum('',[
    'INFO'
])

class Event:

    event_type      : EVENT_TYPE
    menu            : Menu

    def __init__(self, type:EVENT_TYPE):
        self.event_type = type
        self.buttons = []
        self.menu = None

class Loop:

    __time_ticker       : Label

    __is_active         : bool = False
    __pause             : bool = True
    __state             : GAME_STATE
    __display           : Display
    __map_config        : MapConfig
    __config            : Config

    __settings          : Settings
    __map               : Map
    __map_state         : MapState
    __camera            : Camera
    __cvc               : pygame.Surface

    __sel_vert          : Vertex = None
    __sel_cell          : NGon = None

    __popup             : Menu
    __events            : list[Event]
    __bottom_dsp        : StatDisplay
    __pause_menu        : PauseMenu

    def __add_event(self, event_type:EVENT_TYPE,
            text:str=''):
        
        e = Event(event_type)
        def __ok():
            print('MN: OK')
            menu._active = False
            self.__pause = False

        width, height = self.__config.win_dim
        menu = Menu(
            width=width/2, 
            height=height/2)
        lbl = Label(text=text, border_width=0)
        btn = Button(text='OK', width=50, callback=__ok)

        menu.insert(lbl, 0, 1, ALIGN.CENTER)
        menu.insert(btn, 0, 3, ALIGN.CENTER)

        menu.pack()
        e.menu = menu
        
        self.__events.append(e)

    def __handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                match e.key:
                    case pygame.K_ESCAPE: 
                        self.__pause = True
                        self.__pause_menu.show()
                        self.__pause = False

                    case pygame.K_F5: self.__is_active = False
                    case pygame.K_TAB: self.__settings.draw_outline = not self.__settings.draw_outline
                    case _:
                        pass
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                self.__sel_vert = self.__map.select_fuzzed(mx, my)
                print(f'Click: {mx}, {my} | {self.__sel_vert != None}')
            elif e.type == pygame.MOUSEBUTTONUP:
                mx, my = pygame.mouse.get_pos()
                self.__sel_vert = None
                self.__sel_cell = self.__map.select_at(mx, my)

                if self.__state == GAME_STATE.START_SELECT:
                    if self.__sel_cell != None and isinstance(self.__sel_cell.content, Land):
                        self.__state = GAME_STATE.NORMAL
                        self.__map_state.init_cell(self.__sel_cell)
                        self.__add_event(EVENT_TYPE.INFO, f'Species started in {self.__sel_cell.content._climate.name} climate')
            elif e.type == pygame.MOUSEMOTION:
                if self.__sel_vert == None: break
                self.__sel_vert.pos = (e.pos[0], e.pos[1])
                print(f'M: {e.pos[0]}, {e.pos[1]}')
            elif e.type == pygame.MOUSEWHEEL:
                print(e.y)
                self.__camera.inc_zoom(e.y)

    def __render_map_state(self):
        self.__time_ticker.update()

    def __render(self):
        self.__camera.draw(self.__map)
        if self.__sel_cell != None:
            self.__sel_cell.draw(self.__cvc, Color.RED, Color.CYAN)
            b = self.__sel_cell.box
            r = pygame.Rect(b[0], b[1], b[2]-b[0], b[3]-b[1])
            pygame.draw.rect(self.__cvc, Color.WHITE.value, r, 2)
        if self.__state == GAME_STATE.NORMAL:
            self.__render_map_state()
            self.__bottom_dsp.update(self.__sel_cell)

    def __pop_event(self):
        if len(self.__events) == 0:
            return
        e:Event = self.__events[0]
        self.__events = self.__events[1:]
        
        self.__pause = True
        e.menu.show()
        
    def __update(self):
        if self.__map_state.update():
            self.__time_ticker.set_text(self.__frmt_year())

    def __update_menu(self):
        if self.__popup != None:
            self.__popup.update()

    def __loop(self):
        while self.__is_active:
            #self.__display.clear()
            if self.__pause:
                self.__update_menu()
            else:
                self.__handle_events()
                self.__update()
                self.__pop_event()
            self.__render()
            self.__camera.update()

    def __start(self):
        self.__add_event(EVENT_TYPE.INFO,
            text='Choose land to begin at')
        self.__state = GAME_STATE.START_SELECT
        self.__pause = False

    def run(self):
        #self.__display.clear()
        self.__is_active = True
        self.__pause = False
        self.__start()
        self.__loop()

    def __frmt_year(self):
        ret = ''
        yr = self.__map_state.year
        abr = 'B.C' if yr < 0 else 'A.D'
        sfx = ''
        if yr < 100000:
            sfx = 'K'
            yr /= 1000

        return f'{int(yr)}{sfx} {abr}'

    def __init_ui(self):
        dimx, dimy = self.__config.win_dim
        ht = 20
        self.__time_ticker = Label(
            f'Year: {self.__frmt_year()}', 
            fg=Color.WHITE, bg=Color.GREY, 
            pos_y=20, pos_x=75, width=150, 
            border_width=0)
        self.__popup = None

        self.__bottom_dsp = StatDisplay(self.__map_state, 
                                        height=ht,  width=dimx,
                                        pos_y=dimy-ht)
        def __ok():
            self.__pause = False
        def __cancel():
            self.__pause = False
        def __quit():
            self.__is_active = False
            self.__pause = False

        self.__pause_menu = PauseMenu(
            ok_callback=__ok, 
            cancel_callback=__cancel, 
            quit_callback=__quit)

    def __init__(self, map:Map, cfg:MapConfig, stt:Settings) -> None:
        self.__display = get_display()
        self.__cvc = self.__display.get_canvas()
        self.__config = get_config()
        self.__map_config = cfg
        self.__settings = stt
        self.__map = map
        self.__camera = Camera(stt, cfg)
        self.__map_state = MapState()
        self.__events = []
        self.__state = GAME_STATE.NORMAL
        self.__init_ui()

