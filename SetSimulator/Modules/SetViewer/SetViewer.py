import tkinter as tk
from tkinter import ttk
from os import path, makedirs
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
import json
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as anim
import math
import time

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
    
    SAVE_DIRECTORY = 'images'

    # Required for UI scaling
    MIN_WIDTH = 600
    MIN_HEIGHT = 600
    SIDEPANEL_WIDTH = 250
    
    # Required to prevent UI lockup in animation
    MIN_FRAME_DELAY = 1

    def __init_sets(self, setlist):
        if len(setlist) < 1:
            raise IndexError('The set list must contain at least one set.')

        sets = dict()

        for s in setlist:
            if s.name not in sets:
                sets[s.name] = s
        
        self.sets = sets

    def __init__(self, setlist, dimensions=(450,450), iterations=250, colormap='hot', title='Set Viewer', max_interval_delay=1000):
        colormaps = plt.colormaps()
        if colormap not in colormaps:
            raise SetViewer.ColorMapNotIncluded('Color map "%s" is not included in the Matplotlib list of color maps.'%colormap)
        
        if dimensions[0] < SetViewer.MIN_WIDTH:
            raise SetViewer.MinimumWidthExceeded('SetViewer width cannot be less than %d pixels.' % SetViewer.MIN_WIDTH)

        if dimensions[1] < SetViewer.MIN_HEIGHT:
            raise SetViewer.MinimumHeightExceeded('SetViewer height cannot be less than %d pixels.' % SetViewer.MIN_HEIGHT)
        
        self.__init_sets(setlist)

        self.dpi = 100
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.figwidth = self.width / 100
        self.figheight = self.height / 100
        self.figure = plt.figure(figsize=(self.figwidth, self.figheight), dpi=self.dpi)

        # Animation source for the set being generated
        self.anim = None

        # To track where tkinter is during the generation process
        self.after_id = None

        # Root widget
        self.root = tk.Tk()
        self.root.wm_title(title)
        self.root.geometry('%dx%d'%(self.width + SetViewer.SIDEPANEL_WIDTH, self.height))
        self.root.columnconfigure(0, minsize=SetViewer.SIDEPANEL_WIDTH)

        # Main set canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky=tk.E)

        # Left sidepanel frame
        self.sidepanel = tk.LabelFrame(self.root, bd=0)
        self.sidepanel.grid(row=0, column=0, sticky='N')

        # Simulation frame
        self.simulation_frame = tk.LabelFrame(self.sidepanel, text='Simulation', padx=4, pady=4)
        self.simulation_frame.columnconfigure(0, minsize=SetViewer.SIDEPANEL_WIDTH - 40)
        self.simulation_frame.grid(row=0, column=0)

        # Iteration frame
        self.iteration_frame = tk.LabelFrame(self.simulation_frame, bd=0)
        self.iteration_frame.grid(row=0, column=0)

        # Iteration label
        self.iteration_label = tk.Label(self.iteration_frame, text='Iterations:')
        self.iteration_label.grid(row=0, column=0, sticky='S', pady=(0, 4))

        # Iteration slider
        self.iteration_slider = tk.Scale(self.iteration_frame, from_=1, to=iterations, orient=tk.HORIZONTAL)
        self.iteration_slider.set(iterations // 2)
        self.iteration_slider.grid(row=0, column=1)

        # Animation interval frame
        self.interval_frame= tk.LabelFrame(self.simulation_frame, bd=0)
        self.interval_frame.grid(row=1, column=0, pady=(0, 4))

        # Interval label
        self.interval_label = tk.Label(self.interval_frame, text='Delay (MS):')
        self.interval_label.grid(row=0, column=0, sticky='S', pady=(0, 4))

        # Interval slider
        self.interval_slider = tk.Scale(self.interval_frame, from_=SetViewer.MIN_FRAME_DELAY, to=max_interval_delay, orient=tk.HORIZONTAL)
        self.interval_slider.set(max_interval_delay // 2)
        self.interval_slider.grid(row=0, column=1)

        # Set list
        self.set_group = tk.LabelFrame(self.simulation_frame, bd=0)
        self.set_list_label = tk.Label(self.set_group, text='Set:')
        self.set_list_label.grid(row=0, column=0, padx=(0, 8))
        self.set_list = ttk.Combobox(self.set_group, values=list(self.sets.keys()), state='readonly', width=12)
        self.set_list.bind("<<ComboboxSelected>>",lambda e: self.root.focus())
        self.set_list.grid(row=0, column=1)
        self.set_list.current(0)
        self.set_group.grid(row=2, column=0, pady=8)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.simulation_frame, orient=tk.HORIZONTAL, mode='determinate', length=150)
        self.progress_bar.grid(row=3, column=0, pady=8)

        # Generation frame
        self.generation_frame = tk.LabelFrame(self.simulation_frame, bd=0)
        self.generation_frame.grid(row=4, column=0)

        # Generate button
        self.generate_button = tk.Button(self.generation_frame, text='Generate', padx=20, command=self.generate)
        self.generate_button.grid(row=0, column=0, pady=8, padx=4)

        # Stop generation button
        self.cancel_button = tk.Button(self.generation_frame, text='Cancel', padx=20, command=self.stop_generation)
        self.cancel_button.grid(row=0, column=1, pady=8, padx=4)

        # Picture frame
        self.picture_frame = tk.LabelFrame(self.sidepanel, text='Picture')
        self.picture_frame.columnconfigure(0, minsize=SetViewer.SIDEPANEL_WIDTH - 40)
        self.picture_frame.grid(row=1, column=0)

        # Color map
        self.color_map_group = tk.LabelFrame(self.picture_frame, bd=0)
        self.color_map_label = tk.Label(self.color_map_group, text='Color Map:')
        self.color_map_label.grid(row=0, column=0, padx=(0, 8))
        self.color_map_list = ttk.Combobox(self.color_map_group, values=colormaps, state='readonly', width=12)
        self.color_map_list.bind("<<ComboboxSelected>>", self.color_map_changed)
        self.color_map_list.grid(row=0, column=1)
        self.color_map_list.current(colormaps.index(colormap))
        self.color_map_group.grid(row=0, column=0, pady=4, sticky='W')

        # Animation checkbox
        self.animation_check_val = tk.BooleanVar()
        self.animation_checkbox = tk.Checkbutton(self.picture_frame, text='Animation', 
                                                var=self.animation_check_val, command=self.animation_checkbox_clicked)
        self.animation_checkbox.grid(row=1, column=0, padx=(0, 8), pady=2, sticky='W')

        # Save button
        self.save_button = tk.Button(self.picture_frame, text='Save Image', command=self.save_button_handler, padx=32, pady=4, width=8)
        self.save_button.grid(row=3, column=0, pady=8)

        # Close button
        self.close_button = tk.Button(self.sidepanel, text='Close', command=lambda: self.root.quit(), border=2, padx=32, pady=4, width=8)
        self.close_button.grid(row=2, column=0, pady=16, sticky='S')
    
    def save_button_handler(self):
        if not path.exists(SetViewer.SAVE_DIRECTORY):
            makedirs(SetViewer.SAVE_DIRECTORY)
        
        selected_set = self.sets[self.set_list.get()]
        current_time = time.strftime("%Y-%m-%d %I %M %p")
        plt.savefig(SetViewer.SAVE_DIRECTORY + '/%s Set - %s' % (selected_set.name, current_time))
    
    def animation_checkbox_clicked(self):
        self.animation_check_val.set(not self.animation_check_val.get())
    
    def color_map_changed(self, *args):
        selected_set = self.sets[self.set_list.get()]
        if selected_set.set is not None:
            selected_cmap = self.color_map_list.get()
            self.figure.clear()
            self.figure.figimage(selected_set.set['divergence'], cmap=selected_cmap)
            self.canvas.draw()
            
    def render(self, frame, *fargs):
        """ Callback for every frame in animation """
        if self.animation_check_val.get():
            selected_cmap = self.color_map_list.get()
            selected_set, set_, maxIters = fargs

            # Dynamically update animation delay every frame
            delay = self.interval_slider.get()
            self.anim.event_source.interval = delay

            selected_set.set = set_.__next__()[0]
            self.figure.clear()
            self.figure.figimage(selected_set.set['divergence'], cmap=selected_cmap)
            self.progress_bar['value'] = math.ceil(((frame + 1) / maxIters) * 100)
            self.root.update_idletasks()
        else:
            self.anim.event_source.stop()
            self.anim = None
    
    def stop_generation(self):
        # Check if a set is currently being generated
        if self.after_id is not None:
             self.root.after_cancel(self.after_id)
             self.after_id = None
        
        # Stop animation on button click
        if self.anim is not None:
            self.anim.event_source.stop()
            self.anim = None

        self.progress_bar['value'] = 0

    def generate(self):
        """ Handler for the generate button. """
        selected_set = self.sets[self.set_list.get()]
        maxIters = self.iteration_slider.get()
        set_ = iter(selected_set)
        
        # Required helper function to prevent GUI lockup
        def generate_(i=0):
            if i < maxIters:
                delay = self.interval_slider.get()
                selected_set.set = set_.__next__()[0]
                self.progress_bar['value'] = (i / maxIters) * 100
                self.root.update_idletasks()
                self.after_id = self.root.after(delay, lambda: generate_(i+1))
            else:
                selected_cmap = self.color_map_list.get()

                self.figure.clear()
                self.figure.figimage(selected_set.set['divergence'], cmap=selected_cmap)
                self.progress_bar['value'] = 0
                self.canvas.draw()
                self.after_id = None

        self.stop_generation()

        if selected_set.get_template() is None:
            selected_set.generate_template(self.width, self.height)
        
        # Check for animation enabled
        if self.animation_check_val.get():
            delay = self.interval_slider.get()
            self.anim = anim.FuncAnimation(self.figure, self.render, interval=delay, frames=maxIters, repeat=False, blit=False, 
                                            fargs=(selected_set, set_, maxIters))
            self.canvas.draw()

        # Run standard generation without animation if animation is disabled
        else:
            generate_()
                
    def show(self):
        self.root.mainloop()