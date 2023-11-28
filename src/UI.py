from __future__ import annotations
from enum import Enum
from typing import Any, Callable
from pygame import Rect, Surface
import pygame
from colors import Color

from display import Display, get_display

ALIGN = Enum(
        'mode', [
            
            'TOP', 'TOP_LEFT', 'TOP_RIGHT',
            'BOTTOM', 'BOTTOM_LEFT', 'BOTTOM_RIGHT',
            'LEFT', 
            'RIGHT', 
            'CENTER'
        ])

class Control:

    _bounds         : Rect
    _display        : Display
    
    _bg_color       : Color
    _fg_color       : Color
    _border_color   : Color
    _border_width   : int

    _parent         : Control

    def __draw_border(self):

        hb = Rect(self._bounds.left, self._bounds.top, self._bounds.width, self._border_width)
        vb = Rect(self._bounds.left, self._bounds.top, self._border_width, self._bounds.height)

        pygame.draw.rect(self._display.get_canvas(), self._border_color.value, hb)
        pygame.draw.rect(self._display.get_canvas(), self._border_color.value, vb)
        hb.topleft = (hb.left, self._bounds.bottom-self._border_width)
        vb.topleft = (self._bounds.right-self._border_width, vb.top)
        pygame.draw.rect(self._display.get_canvas(), self._border_color.value, hb)
        pygame.draw.rect(self._display.get_canvas(), self._border_color.value, vb)

    def in_bounds(self, x:int, y:int):
        return self._bounds.collidepoint(x, y)

    def is_collide(self, rect:Rect):
        return self._bounds.colliderect(rect)

    def update(self):
        if self._bg_color != None:
            pygame.draw.rect(self._display.get_canvas(), self._bg_color.value, self._bounds)
        if self._border_width > 0:
            self.__draw_border()

    def move(self, x:int, y:int, align:ALIGN=ALIGN.TOP_LEFT):
        
        match align:
            case ALIGN.TOP_LEFT: self._bounds.topleft = (x, y)
            case ALIGN.TOP_RIGHT: self._bounds.topright = (x, y)
            case ALIGN.TOP: 
                self._bounds.top = y
                self._bounds.centerx = x

            case ALIGN.BOTTOM_LEFT: self._bounds.bottomleft = (x, y)
            case ALIGN.BOTTOM_RIGHT: self._bounds.bottomright = (x, y)
            case ALIGN.BOTTOM:
                self._bounds.bottom = y
                self._bounds.centerx = x

            case ALIGN.LEFT: 
                self._bounds.left = x
                self._bounds.centery = y
            case ALIGN.RIGHT: 
                self._bounds.right = x
                self._bounds.centery = y

            case ALIGN.CENTER: self._bounds.center = (x, y)

    def __init__(self,
                 width = 0, height = 0,
                 pos_x = 0, pos_y = 0,
                 border_width:int=3,
                 fg=Color.WHITE, bg=Color.BLACK, border:Color=Color.LIGHT_GRAY,
                 parent:Control = None
                 ):
        self._bounds = Rect(pos_x, pos_y, width, height)
        self._display = get_display()
        self._border_color = border
        self._border_width = border_width
        self._parent = parent
        self._fg_color = fg
        self._bg_color = bg

class Label(Control):
    
    __font_size     : int
    __font          : str
    __text          : Surface
    
    def set_text(self, text:str):
        font = pygame.font.SysFont(self.__font, self.__font_size)
        self.__text = font.render(text, False, self._fg_color.value)
        self._bounds.width = self.__text.get_width()
        self._bounds.height = self.__text.get_height()

    def update(self):
        super().update()
        self._display.get_canvas().blit(self.__text, self._bounds.topleft)

    def move(self, x: int, y: int, align:ALIGN=ALIGN.TOP_LEFT):
        super().move(x, y, align)
        self._bounds.width = self.__text.get_width()
        self._bounds.height = self.__text.get_height()

    def __init__(self, 
                 text='', font='arial',
                 width=0, height=0, 
                 pos_x=0, pos_y=0,
                 border_width:int=3,
                 fg=Color.WHITE, bg=Color.BLACK, border: Color = Color.LIGHT_GRAY, 
                 font_size:int=20,
                 parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, fg, bg, border, parent)
        self.__font = font
        self.__font_size = font_size
        self.set_text(text)
        self.move(pos_x, pos_y, align=ALIGN.CENTER)

class Clickable(Control):

    __callback      : Callable

    def on_click(self):
        pass

    def __init__(self, width=0, height=0, pos_x=0, pos_y=0, 
                 border_width: int = 3, fg=Color.WHITE, bg=Color.BLACK, 
                 border: Color = Color.LIGHT_GRAY, parent: Control = None,
                 callback:Callable=None):
        super().__init__(width, height, pos_x, pos_y, border_width, fg, bg, border, parent)
        self.__callback = callback

class Button(Clickable):

    label: Label

    def update(self):
        super().update()
        self.label.update()

    def move(self, x: int, y: int):
        super().move(x, y, ALIGN.CENTER)
        self.label.move(x, y, ALIGN.CENTER)

    def __init__(self, width=0, height=0, pos_x=0, pos_y=0, 
                 border_width: int = 3, fg=Color.WHITE, bg=Color.BLACK, 
                 border: Color = Color.LIGHT_GRAY, parent: Control = None, 
                 text='', pad:int=3, callback: Callable[..., Any] = None):
        super().__init__(width, height, pos_x, pos_y, border_width, fg, bg, border, parent, callback)
        self.label = Label(text, fg=fg, border_width=0, bg=None, parent=self)
        
        self._bounds.width = max(self.label._bounds.width, self._bounds.width)
        self._bounds.height = max(self.label._bounds.height, self.label._bounds.height)

        self._bounds.width += pad*2
        self._bounds.height += pad*2

class ProgressBar(Control):

    pass

class Container(Control):

    class Box:
        content         : Control
        x               : int
        y               : int
        align           : Container.ALIGN

        def __init__(self, content, x:int, y:int, align:Container.ALIGN):
            self.content = content
            self.x = x
            self.y = y
            self.align = align

    __children          : list[Container.Box]

    def update(self):
        super().update()
        for c in self.__children:
            c.content.update()

    def insert(self, ctrl:Control, x:int, y:int, align:ALIGN=ALIGN.LEFT):
        box = Container.Box(ctrl, x, y, align)
        self.__children.append(box)

    def pack(self):
        g_w = max(t.x for t in self.__children)
        g_h = max(t.y for t in self.__children)
        b_w = self._bounds.width
        b_h = self._bounds.height

        d_w = b_w/(g_w+1)
        d_h = b_h/(g_h+1)

        for c in self.__children:
            ref = Rect(self._bounds.left+d_w*c.x, self._bounds.top+d_h*c.y, d_w, d_h)
            match c.align:
                case ALIGN.LEFT: 
                    c.content.move()
                case ALIGN.RIGHT: pass
                case ALIGN.TOP: pass
                case ALIGN.BOTTOM: pass
                case ALIGN.CENTER: c.content.move(ref.centerx, ref.centery)


    def __init__(self, width=0, height=0, 
                 pos_x=0, pos_y=0, 
                 border_width:int=3,
                 fg=Color.WHITE, bg=Color.BLACK, border: Color = Color.LIGHT_GRAY, 
                 parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, fg, bg, border, parent)
        self.__children = []

