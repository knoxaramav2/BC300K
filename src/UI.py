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
    _padx           : int
    _pady           : int

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
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, border:Color=Color.LIGHT_GRAY,
                 parent:Control = None
                 ):
        self._bounds = Rect(pos_x, pos_y, width+padx*2, height+pady*2)
        self._display = get_display()
        self._border_color = border
        self._border_width = border_width
        self._parent = parent
        self._fg_color = fg
        self._bg_color = bg
        self._padx = padx
        self._pady = pady

class Writeable(Control):

    __font_size     : int
    __font          : str
    __text          : Surface
    _value          : str
    _const          : CONSTRAINT

    CONSTRAINT = Enum(
        'constraint', [
            'NUM', 'ALPHA', 'ALPHANUM'
        ]
    )

    def set_text(self, text:str):

        if self._const == Writeable.CONSTRAINT.ALPHANUM:
            if not text.isalnum() and text!= '': return
        elif self._const == Writeable.CONSTRAINT.ALPHA:
            if not text.isalpha() and text!= '': return
        elif self._const == Writeable.CONSTRAINT.NUM:
            if not text.isnumeric() and text!= '': return

        self._value = text
        font = pygame.font.SysFont(self.__font, self.__font_size)
        self.__text = font.render(text, False, self._fg_color.value)

    def on_backspace(self):
        if self._value == '': return
        self.set_text(self._value[:-1])

    def on_type(self, char:str):
        self.set_text(self._value + char)
    
    def update(self):
        super().update()
        self._display.get_canvas().blit(self.__text, (self._bounds.left+self._padx, self._bounds.top-self._pady*2))

    def move(self, x: int, y: int, align:ALIGN=ALIGN.TOP_LEFT):
        super().move(x, y, align)

    def __init__(self, width=0, height=0, pos_x=0, pos_y=0, 
                 font:str='arial', font_size:int=20, text:str='',
                 border_width: int = 3, 
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, 
                 const:CONSTRAINT=CONSTRAINT.ALPHANUM,
                 border: Color = Color.LIGHT_GRAY, parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent)

        self._const = const
        self.__font = font
        self.__font_size = font_size
        self.set_text(text)

        if width == 0: self._bounds.width = self.__text.get_width()+(padx*2)
        else: self._bounds.width = width+(padx*2)
        
        if height == 0: self._bounds.height = self.__text.get_height()+(pady*2)
        else: self._bounds.height = height+(pady*2)

        self.move(pos_x, pos_y, align=ALIGN.LEFT)

class Text(Writeable):

    pass

class Label(Control):
    
    __font_size     : int
    __font          : str
    __text          : Surface
    
    def set_text(self, text:str):
        font = pygame.font.SysFont(self.__font, self.__font_size)
        self.__text = font.render(text, False, self._fg_color.value)

    def update(self):
        super().update()
        self._display.get_canvas().blit(self.__text, self._bounds.topleft)

    def move(self, x: int, y: int, align:ALIGN=ALIGN.CENTER):
        super().move(x, y, align)

    def __init__(self, 
                 text='', font='arial',
                 width=0, height=0, 
                 pos_x=0, pos_y=0,
                 border_width:int=3,
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, border: Color = Color.LIGHT_GRAY, 
                 font_size:int=20,
                 parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent)
        self.__font = font
        self.__font_size = font_size
        self.set_text(text)

        if width == 0: self._bounds.width = self.__text.get_width()+(padx*2)
        else: self._bounds.width = width+(padx*2)
        
        if height == 0: self._bounds.height = self.__text.get_height()+(pady*2)
        else: self._bounds.height = height+(pady*2)

        self.move(pos_x, pos_y, align=ALIGN.CENTER)

class Clickable(Control):

    __callback      : Callable

    def set_callback(self, callback:Callable):
        self.__callback = callback

    def on_click(self):
        if self.__callback != None:
            self.__callback()

    def __init__(self, width=0, height=0, pos_x=0, pos_y=0, 
                 border_width: int = 3, 
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, 
                 border: Color = Color.LIGHT_GRAY, parent: Control = None,
                 callback:Callable=None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent)
        self.__callback = callback

class CheckBox(Clickable):

    _value          : bool
    _check_color    : Color
    _uncheck_color  : Color
    _label          : Label

    def update(self):
        super().update()
        self.label.update()

    def move(self, x: int, y: int):
        super().move(x, y, ALIGN.CENTER)
        self.label.move(x, y, ALIGN.CENTER)

    def __init__(self, width=10, height=10, pos_x=0, pos_y=0, 
                 value:bool = False,
                 border_width: int = 3,
                 padx:int=0, pady:int=0, 
                 fg=Color.WHITE, border: Color = Color.LIGHT_GRAY, 
                 parent: Control = None, callback: Callable[..., Any] = None,
                 check_color:Color=Color.GREEN, uncheck_color:Color = Color.GREY,
                 text:str=''):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, uncheck_color, border, parent, callback)
        self.label = Label(text, fg=fg, border_width=0, bg=None, parent=self)
        
        self._bounds.width = max(self.label._bounds.width, self._bounds.width)
        self._bounds.height = max(self.label._bounds.height, self.label._bounds.height)
        
        self._value = value
        self._check_color = check_color
        self._uncheck_color = uncheck_color

    def on_click(self):
        super().on_click()
        self._value = not self._value
        self._bg_color = self._check_color if self._value else self._uncheck_color

    def set(self, val:bool):
        self._value = val

    def get(self):
        return self._value

class Button(Clickable):

    label: Label

    def update(self):
        super().update()
        self.label.update()

    def move(self, x: int, y: int):
        super().move(x, y, ALIGN.CENTER)
        self.label.move(x, y, ALIGN.CENTER)

    def __init__(self, width=0, height=0, pos_x=0, pos_y=0, 
                 border_width: int = 3, 
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, 
                 border: Color = Color.LIGHT_GRAY, parent: Control = None, 
                 text='', pad:int=3, callback: Callable[..., Any] = None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent, callback)
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

    _children          : list[Container.Box]

    def update(self):
        super().update()
        for c in self._children:
            c.content.update()

    def insert(self, ctrl:Control, x:int, y:int, align:ALIGN=ALIGN.LEFT):
        box = Container.Box(ctrl, x, y, align)
        self._children.append(box)

    def pack(self):
        g_w = max(t.x for t in self._children)
        g_h = max(t.y for t in self._children)
        b_w = self._bounds.width
        b_h = self._bounds.height

        d_w = b_w/(g_w+1)
        d_h = b_h/(g_h+1)

        for c in self._children:
            ref = Rect(self._bounds.left+d_w*c.x, self._bounds.top+d_h*c.y, d_w, d_h)
            match c.align:
                case ALIGN.TOP: c.content.move(ref.centerx, ref.top)
                case ALIGN.TOP_LEFT:c.content.move(ref.left, ref.top)
                case ALIGN.TOP_RIGHT:c.content.move(ref.right, ref.top)

                case ALIGN.BOTTOM: c.content.move(ref.centerx, ref.bottom)
                case ALIGN.BOTTOM_LEFT: c.content.move(ref.left, ref.bottom)
                case ALIGN.BOTTOM_RIGHT: c.content.move(ref.right, ref.bottom)

                case ALIGN.CENTER: c.content.move(ref.centerx, ref.centery)
                case ALIGN.LEFT: c.content.move(ref.left, ref.centery)
                case ALIGN.RIGHT: c.content.move(ref.right, ref.centery)

    def __init__(self, width=0, height=0, 
                 pos_x=0, pos_y=0, 
                 border_width:int=3,
                 padx:int=0, pady:int=0,
                 fg=Color.WHITE, bg=Color.BLACK, border: Color = Color.LIGHT_GRAY, 
                 parent: Control = None):
        super().__init__(width, height, pos_x, pos_y, border_width, padx, pady, fg, bg, border, parent)
        self._children = []

