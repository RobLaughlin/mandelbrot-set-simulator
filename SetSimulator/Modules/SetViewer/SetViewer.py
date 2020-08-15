import tkinter as tk
from tkinter import ttk
from os import path
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
import json
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

from ..ComplexSets.ComplexSet import ComplexSet as Set
from ..ComplexSets.CoordinateRange import CoordinateRange as crange 
from ..ComplexSets.Sets.Mandelbrot import Mandelbrot

class SetViewer(object):
    """
    GUI Controller/SetViewer for sets. Includes a save button with set selector and colormap selector.
    There is a checkbox included for enabling or disabling animated set generation.
    The set simulation can be started, zoomed in and out by clicking the set view area.
    """

    class MinimumWidthExceeded(Exception):
        pass

    class MinimumHeightExceeded(Exception):
        pass
    
    class ColorMapNotIncluded(Exception):
        pass

    # This is required due to the length of the toolbar.
    MIN_WIDTH = 450
    MIN_HEIGHT = 200
    TOOLBAR_HEIGHT = 32

    def __init_sets(self, setlist):
        if len(setlist) < 1:
            raise IndexError('The set list must contain at least one set.')

        sets = dict()

        for s in setlist:
            if s.name not in sets:
                sets[s.name] = s
        
        self.sets = sets

    def __init__(self, setlist, save_icon, dimensions=(450,450), colormap='gray', title='Set Viewer'):
        colormaps = plt.colormaps()
        if colormap not in colormaps:
            raise SetViewer.ColorMapNotIncluded('Color map "%s" is not included in the Matplotlib list of color maps.'%colormap)
        
        if dimensions[0] < SetViewer.MIN_WIDTH:
            raise SetViewer.MinimumWidthExceeded('SetViewer width cannot be less than %d pixels.' % SetViewer.MIN_WIDTH)

        if dimensions[1] < SetViewer.MIN_HEIGHT:
            raise SetViewer.MinimumHeightExceeded('SetViewer height cannot be less than %d pixels.' % SetViewer.MIN_HEIGHT)
        
        if not path.exists(save_icon):
            raise FileNotFoundError('Save icon "%s" does not exist.'%save_icon)
        
        self.__init_sets(setlist)

        self.dpi = 100
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.figwidth = self.width / 100
        self.figheight = self.height / 100
        self.figure = plt.figure(figsize=(self.figwidth, self.figheight), dpi=self.dpi)

         # All Tkinter widgets in the SetViewer
        self.root = tk.Tk()
        self.save_button = None
        self.set_list_label = None
        self.set_list = None
        self.color_map_label = None
        self.color_map_list = None
        self.animation_checkbox = None
        self.generate_button = None
        
        self.root.wm_title(title)
        self.root.geometry('%dx%d'%(self.width, self.height  + SetViewer.TOOLBAR_HEIGHT))

        # Save button
        self.save_img = ImageTk.PhotoImage(Image.open(save_icon), master=self.root)
        self.save_button = tk.Button(
            self.root, image=self.save_img, border=2, padx=4, pady=4, 
            width=SetViewer.TOOLBAR_HEIGHT, height=SetViewer.TOOLBAR_HEIGHT)
        self.save_button.grid(row=0, column=0, padx=(0, 8))

        # Set list combobox
        self.set_list_label = tk.Label(self.root, text='Set:')
        self.set_list_label.grid(row=0, column=1, padx=(0, 8))
        self.set_list = ttk.Combobox(self.root, values=list(self.sets.keys()), state='readonly', width=12)
        self.set_list.bind("<<ComboboxSelected>>",lambda e: self.root.focus())
        self.set_list.grid(row=0, column=2)
        self.set_list.current(0)

        # Color map combobox
        self.color_map_label = tk.Label(self.root, text='Color Map:')
        self.color_map_label.grid(row=0, column=3, padx=8)
        self.color_map_list = ttk.Combobox(self.root, values=colormaps, state='readonly', width=12)
        self.color_map_list.bind("<<ComboboxSelected>>",lambda e: self.root.focus())
        self.color_map_list.grid(row=0, column=4)
        self.color_map_list.current(colormaps.index(colormap))

        # Animation checkbox
        self.animation_checkbox = tk.Checkbutton(self.root, text='Animation')
        self.animation_checkbox.grid(row=0, column=5, padx=8)

    def show(self):
        selected_set = self.sets[self.set_list.get()]
        selected_cmap = self.color_map_list.get()

        if selected_set.get_template() is None:
            selected_set.generate_template(self.width, self.height)
            
        if selected_set.set is None:
            selected_set.generate_set()
        
        self.figure.figimage(selected_set.set['divergence'], cmap=selected_cmap)
        canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        canvas.get_tk_widget().grid(row=1, column=0, columnspan=6)
        canvas.draw()

        self.root.mainloop()

        

"""
from . import Set, CoordinateRange
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import tkinter
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import atexit

class SetViewer(Set):
    def __init__(self, iterations:int, coord_range:CoordinateRange, figsize=(8,8), dpi=100):
        
        GUI inherited class of the Mandelbrot set. 
        Displays the Mandelbrot set visually using pyplot.

        Params in addition to the Mandelbrot class:
        figsize (x, y) - Size of the figure in inches
        dpi - pixels per inch

        ex: figsize=(8,8) dpi=100 yields a 800x800 pixel figure.
        

        super().__init__(iterations=iterations, coord_range=coord_range)
        self.figsize = figsize
        self.dpi = dpi

        self.root = tkinter.Tk()
        self.root.wm_title('Mandelbrot Set SetViewer')
        self.__figure = plt.figure(figsize=figsize, dpi=dpi)

    def show(self, colormap='gray', aspect_ratio='auto'):
        if self.set_template is None:
            self.generate_template(int(self.figsize[0] * self.dpi), int(self.figsize[1] * self.dpi))
            
        if self.set is None:
            self.generate_set()

        self.__figure.figimage(self.set['divergence'], cmap=colormap)
        canvas = FigureCanvasTkAgg(self.__figure, master=self.root)
        canvas.get_tk_widget().pack()
        canvas.draw()

        tkinter.Button(self.root, text="Close", command=self.__onclose).pack()
        self.root.mainloop()

    def __onclose(self):
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
"""