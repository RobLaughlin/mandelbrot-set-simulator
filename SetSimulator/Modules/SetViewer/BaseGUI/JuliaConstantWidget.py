import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable
from .LabeledWidget import LabeledWidget

class JuliaComplexPart(LabeledWidget):
    """The real or imaginary part widgets for the Julia constant widget.
    
    Args:
        master (tkinter.widget): Container of the real/imaginary part widgets.
        const_range (tuple) (float, float): Minimum and maximum for the part range, respecitvely.
        handler (function(JuliaComplexPart)): Event handler for when the part widget is changed.
        grid_index (tuple) (int, int): Location on the tkinter grid system.
        default_value (int): The default value of the part widget.
    
    """
    def __init__(self, master:tk.Widget, const_range:tuple, handler:Callable, text:str, grid_index:tuple, default_value=0):
        opts = {'from_': const_range[0], 'to': const_range[1], 'orient': tk.HORIZONTAL, 'length': 150,
        'digits': 8, 'resolution': 0.000001, 'command': lambda event: handler(self)}

        super().__init__(master, (tk.Scale, opts), text, grid_index)
        self.val = default_value

class JuliaConstantWidget(tk.LabelFrame):
    """The container widget for the complex constant used in generating the Julia set.

    Args:
        master (tkinter.widget): Container of the Julia set constant widget.
        widget_params (dict[str, object]): Widget-specific configuration.
        minwidth (int): The minimum width if the Julia constant widget.
        grid_index (tuple) (int, int): The respective (row, column) position on the tkinter grid.
    
    Attributes:
        real_part (juliaconstantwidget.juliacomplexpart): The real part widget of the Julia set constant.
        imag_part (juliaconstantwidget.juliacomplexpart): The imaginary part widget of the Julia set constant.
    
    Widget Args:
        real_handler (function(JuliaComplexPart)): Event handler for when the real part widget is changed.
        real_range (tuple) (float, float): Respective minimum and maximum for the real range.
        imag_handler (function(JuliaComplexPart)): Event handler for when the imaginary part widget is changed.
        imag_range (tuple) (float, float): Respective minimum and maximum for the imaginary range.
        default_value (complex): Complex number to use as the default selected constant for the Julia set widget.
    
    """
    def __init__(self, master:tk.Widget, widget_params:Dict[str, object], minwidth:int):
        super().__init__(master, text='Julia Constant')
        self.columnconfigure(0, minsize=minwidth)

        real_handler = widget_params['real_handler']
        real_range = widget_params['real_range']
        imag_handler = widget_params['imag_handler']
        imag_range = widget_params['imag_range']
        default_value = widget_params['default_value']

        self._real_part = JuliaComplexPart(self, real_range, real_handler, 'Real:', (0, 0), default_value.real)
        self._imag_part = JuliaComplexPart(self, imag_range, imag_handler, 'Imag:', (1, 0), default_value.imag)

    def hide(self):
        self.grid_remove()
    
    def show(self):
        self.grid()