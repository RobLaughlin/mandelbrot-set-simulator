import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import pyplot as plt
from os import path
from PIL import Image, ImageTk
from typing import Callable

class Canvas(FigureCanvasTkAgg):
    """Main canvas for viewing the complex set generation/image.
    
    Args:
        master (tkinter.widget): Parent container of the canvas.
        handler (function(widget, event)): The event handler for the canvas click event.
        size (tuple) (int, int): Width and height of the canvas, respectively.
        fpath (str): File path of the default image to load onto the canvas.
        dpi (int, optional): DPI of the figure, default is 100.
    
    Attributes:
        width (int): Width (in pixels) of the canvas.
        height (int): Height (in pixels) of the canvas.
        figure (matplotlib.pyplot.figure): Pyplot figure of the canvas.
    
    """
    def __init__(self, master:tk.Widget, handler:Callable, size:tuple, fpath:str, dpi=100):
        self._width = size[0]
        self._height = size[1]
        self._figure = plt.figure(figsize=(self._width / dpi, self._height / dpi), dpi=dpi)
        super().__init__(self._figure, master=master)
        self.load_default_figure(fpath)
        self.mpl_connect('button_press_event', lambda event: handler(self, event))

    @property
    def width(self) -> int:
        """int: Width of the canvas."""
        return self._width

    @property
    def height(self) -> int:
        """int: Height of the canvas."""
        return self._height

    @property
    def figure(self) -> plt.figure:
        """matplotlib.pyplot.figure: Figure of the canvas."""
        return self._figure

    @figure.setter
    def figure(self, figure:plt.figure):
        self._figure = figure
    
    def load_default_figure(self, fpath:str):
        """Load the default image into figure when the GUI loads.
        
        Args:
            fpath (str): File path of the default image to load onto the canvas.
        
        Raises:
            FileNotFoundError: If the default image to load is not found.
        
        """
        if not path.exists(fpath):
            raise FileNotFoundError('%s File not found.' % fpath)
        
        img = Image.open(fpath)

        # Pad image with emptiness
        new_img = Image.new('RGBA', (self._width, self._height), 'white')
        offset_width = (self._width - img.width) // 2
        offset_height = (self._height - img.height) // 2
        new_img.paste(img, (offset_width, offset_height))
        
        self.update(new_img)
    
    def update(self, img:Image, cmap='gray', origin='lower', redraw=False):
        self._figure.clear()
        self._figure.figimage(img, cmap=cmap, origin=origin)
        if redraw:
            self.draw()