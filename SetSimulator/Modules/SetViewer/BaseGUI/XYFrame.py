import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable
from .LabeledWidget import LabeledWidget
from ...ComplexSets.CoordinateRange import CoordinateRange as crange

class RangeFrame(tk.Frame):
    """Coordinate Range container between a minimum and maximum value.

    Args:
        master (tkinter.widget): The container of the range frame.
        validate (function(key, entry)): Validation event when a key is entered.
        grid_index (tuple): (int, int) Row and column position on the tkinter grid.
        text (str): Text of each minumum and maximum label.
    
    Attributes:
        min (labeledwidget): Widget container for minimum value in the specified range.
        max (labeledwidget): Widget container for maximum value in the specified range.
    
    """
    def __init__(self, master:tk.Widget, validate:Callable, grid_index:tuple, coord_range:tuple, text:str):
        super().__init__(master)
        self.grid(row=grid_index[0], column=grid_index[1], pady=4)
        
        opts = {'width': 8, 'validate': 'key', 'validatecommand': validate}
        self._min = LabeledWidget(self, (tk.Entry, opts), text + ' Min:', (0, 0))
        self._min.grid_configure(padx=4)
        self._max = LabeledWidget(self, (tk.Entry, opts), text + ' Max:', (0, 1))
        self._max.grid_configure(padx=4)
        self._min.val = coord_range[0]
        self._max.val = coord_range[1]
        
    @property
    def min(self) -> LabeledWidget:
        """labeledwidget: Minimum value in range."""
        return self._min
    
    @property
    def max(self) -> LabeledWidget:
        """"labeledwidget: Maximum value in range."""
        return self._max

class XYFrame(tk.LabelFrame):
    """XY Coordinate range frame.

    Args:
        master (tkinter.widget): The container of the XY frame.
        widget_params (dict[str, object]): Widget-specific arguments.
        minwidth (int): Minimum width of the XY frame.
    
    Attributes:
        x_range (xyframe.rangeframe): The container widget for the x_min and x_max LabeledWidgets.
        y_range (xyframe.rangeframe): The container widget for the y_min and y_max LabeledWidgets.
        coord_range (coordinaterange): The validated coordinate range of the XY widgets.
    
    Widget Args:
        coord_range (CoordinateRange): Full XY coordinate range.
        validate (function): Keystroke validation function on each x&y component.
    
    """
    def __init__(self, master:tk.Widget, widget_params:Dict[str, object], minwidth:int):
        super().__init__(master, text='XY Coordinate Range')
        self.columnconfigure(0, minsize=minwidth)

        xr = widget_params['coord_range'].get_xRange()
        yr = widget_params['coord_range'].get_yRange()
        validate = widget_params['validate']
        
        self._x_range = RangeFrame(self, validate, (0, 0), xr, 'X')
        self._y_range = RangeFrame(self, validate, (1, 0), yr, 'Y')
    
    @property
    def x_range(self) -> RangeFrame:
        """ X min/max coordinate range subcomponent."""
        return self._x_range
    
    @property
    def y_range(self) -> RangeFrame:
        """ Y min/max coordinate range subcomponent."""
        return self._y_range
    
    @property
    def coord_range(self) -> crange: 
        """Returns a XY CoordinateRange if both the X and Y ranges are valid.

        Returns:
            coordinaterange: The validated coordinate object of the XY range.
            coordinaterange.invalidcoordinatebounds: If the validation of range(s) fails.
            ValueError: If the characters typed in the XY range fields are not valid floats.
        
        """
        coords = None
        try:
            minX = float(self.x_range.min.val)
            maxX = float(self.x_range.max.val)
            minY = float(self.y_range.min.val)
            maxY = float(self.y_range.max.val)
            coords = crange(minX, maxX, minY, maxY)
        except crange.InvalidCoordinateBounds as err:
            return err
        except ValueError as err:
            return err
        return coords
    
    def update_all(self, coord_range:crange):
        x_range = coord_range.get_xRange()
        y_range = coord_range.get_yRange()

        self._x_range.min.val = x_range[0]
        self._x_range.max.val = x_range[1]
        self._y_range.min.val = y_range[0]
        self._y_range.max.val = y_range[1]
        return self.coord_range