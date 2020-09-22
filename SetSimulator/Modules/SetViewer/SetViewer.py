import tkinter as tk
from tkinter import ttk
from os import path, makedirs
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as anim
import webbrowser
import time
import copy

from ..ComplexSets.ComplexSet import ComplexSet as Set
from ..ComplexSets.CoordinateRange import CoordinateRange as crange 
from ..ComplexSets.Sets.Mandelbrot import Mandelbrot
from .BaseGUI.BaseGUI import BaseGUI

class SetViewer(BaseGUI):
    """
    GUI Controller/SetViewer for sets. Includes a save button with set selector and colormap selector.
    There is a checkbox included for enabling or disabling animated set generation.
    The set simulation can be started, zoomed in and out by clicking the set view area.
    """

    def __init_sets(self, setlist, dimensions):
        if len(setlist) < 1:
            raise IndexError('The set list must contain at least one set.')

        sets = dict()

        for s in setlist:
            if s.name not in sets:
                if s.get_template() is None:
                    s.generate_template(dimensions[0], dimensions[1])

                sets[s.name] = s
        
        self.sets = sets
        self.selected_set = iter(copy.deepcopy(setlist[0]))

    def __init__(self, setlist, dimensions=(600,600), iterations=250, colormap='hot', title='Set Viewer', max_interval_delay=1000):
        self.__init_sets(setlist, dimensions)
        super().__init__(self.sets, setlist[0].get_coord_range(), dimensions, iterations, colormap, title, max_interval_delay)
        
        # For depth of zoom on canvas
        self.zoom_level = 0

        # Animation source for the set being generated
        self.anim = None

        # To track where tkinter is during the generation process
        self.after_id = None
        # Set zoom handler
        self.canvas.mpl_connect('button_press_event', self.canvas_onclick)

    def update_xyrange_entries(self, coord_range:crange):
        x_range = coord_range.get_xRange()
        y_range = coord_range.get_yRange()

        self.min_x_entry.delete(0, tk.END)
        self.min_x_entry.insert(0, str(x_range[0]))

        self.max_x_entry.delete(0, tk.END)
        self.max_x_entry.insert(0, str(x_range[1]))

        self.min_y_entry.delete(0, tk.END)
        self.min_y_entry.insert(0, str(y_range[0]))

        self.max_y_entry.delete(0, tk.END)
        self.max_y_entry.insert(0, str(y_range[1]))

    def canvas_onclick(self, event):
        """ Handler for clicking the set canvas """

        # Handle which button was pressed
        btn_pressed = str(event.button)
        if btn_pressed == 'MouseButton.LEFT':
            self.zoom_level += 1
        elif btn_pressed == 'MouseButton.RIGHT':
            self.zoom_level -= 1
        
        # Some zoom math
        x_range = self.selected_set.get_coord_range().get_xRange()
        y_range = self.selected_set.get_coord_range().get_yRange()
        x_len = abs(x_range[1] - x_range[0])
        y_len = abs(y_range[1] - y_range[0])
        rel_x = x_range[0] + x_len * (event.x / self.width)
        rel_y = y_range[0] + y_len * (event.y / self.height)
        rel_zoom = (0.5**self.zoom_level)

        new_crange = crange(rel_x - rel_zoom, rel_x + rel_zoom, rel_y - rel_zoom, rel_y + rel_zoom)
        self.update_xyrange_entries(new_crange)
        self.generate_wrapper()

    def range_entry_handler(self, key, entry):
        try:
            float(entry)
        except:
            if entry != '':
                return False
        
        return True
    
    def save_button_handler(self):
        if not path.exists(SetViewer.SAVE_DIRECTORY):
            makedirs(SetViewer.SAVE_DIRECTORY)
        
        current_time = time.strftime("%Y-%m-%d %I %M %p")
        plt.savefig(SetViewer.SAVE_DIRECTORY + '/%s Set - %s' % (self.selected_set.name, current_time))
    
    def set_list_changed(self):
        self.root.focus()

    def animation_checkbox_clicked(self):
        self.animation_check_val.set(not self.animation_check_val.get())
        self.stop_generation(clear=False)
    
    def color_map_changed(self, *args):
        if self.selected_set.get_set() is not None:
            selected_cmap = self.color_map_list.get()
            self.update_canvas(cmap=selected_cmap)
            self.canvas.draw()
    
    def update_canvas(self, cmap):
        self.figure.clear()
        self.figure.figimage(self.selected_set.get_set()['divergence'], cmap=cmap, origin='lower')

    def render(self, frame):
        """ Callback for every frame in animation """
        if self.animation_check_val.get():
            selected_cmap = self.color_map_list.get()
            
            # Dynamically update animation delay every frame
            delay = self.interval_slider.get()
            self.anim.event_source.interval = delay

            try:
                self.selected_set.__next__()
                self.update_canvas(cmap=selected_cmap)
                self.update_progress()
            except StopIteration:
                selected_cmap = self.color_map_list.get()
                self.update_canvas(cmap=selected_cmap)
                self.canvas.draw()
                self.stop_generation()
                self.pause_button['state'] = 'disabled'
                self.pause_button['text'] = 'Pause'
        else:
            self.anim.event_source.stop()
    
    def continue_generation(self):
        self.generate_wrapper(reset=False)

    def pause_generation(self):
        clear = True if self.selected_set.get_current_iteration() >= self.selected_set.get_iterations() else False
        selected_cmap = self.color_map_list.get()

        self.stop_generation(clear=clear)
        self.pause_button.config(command=self.continue_generation)
        self.pause_button['text'] = 'Continue'
        self.update_canvas(cmap=selected_cmap)
        if not self.animation_check_val.get():
            self.canvas.draw()
        
    def stop_generation(self, clear=True):
        # Check if a set is currently being generated
        if self.after_id is not None:
             self.root.after_cancel(self.after_id)
        
        # Stop animation on button click
        if self.anim is not None:
            self.anim.event_source.stop()

        self.update_progress(clear=clear)

    def validate_range_entries(self):
        coords = None
        try:
            minX = float(self.min_x_entry.get())
            maxX = float(self.max_x_entry.get())
            minY = float(self.min_y_entry.get())
            maxY = float(self.max_y_entry.get())
            coords = crange(minX, maxX, minY, maxY)
        except crange.InvalidCoordinateBounds as err:
            tk.messagebox.showerror(title='Invalid Coordinate Bounds', message=err)
            return
        except ValueError:
            tk.messagebox.showerror(title='Value Error', message="Invalid XY Range values.")
            return
        
        return coords

    def update_progress(self, clear=False):
        if clear:
            self.progress_bar['value'] = 0
        else:
            self.progress_bar['value'] = (self.selected_set.get_current_iteration() / self.selected_set.get_iterations()) * 100

        self.root.update_idletasks()
        
    def generate(self):
        try:
            delay = self.interval_slider.get()
            self.selected_set.__next__()
            self.update_progress()
            self.after_id = self.root.after(delay, self.generate)
        except StopIteration:
            selected_cmap = self.color_map_list.get()
            self.stop_generation()
            self.update_canvas(cmap=selected_cmap)
            self.canvas.draw()
            self.pause_button['state'] = 'disabled'
            self.pause_button['text'] = 'Pause'
            
    def generate_wrapper(self, reset=True):
        """ Handler for the generate button. """
        self.pause_button.config(command=self.pause_generation)
        self.pause_button['state'] = 'active'
        self.pause_button['text'] = 'Pause'
        self.stop_generation()

        coords = self.validate_range_entries()
        maxIters = self.iteration_slider.get()

        if reset:
            selected_set = copy.deepcopy(self.sets[self.set_list.get()])
            selected_set.set_coord_range(coords)
            selected_set.set_iterations(maxIters)
            self.selected_set = iter(selected_set)
        
        # Check for animation enabled
        if self.animation_check_val.get():
            delay = self.interval_slider.get()
            self.anim = anim.FuncAnimation(self.figure, self.render, interval=delay, 
                                            repeat=False, blit=False, cache_frame_data=False)
            self.canvas.draw()
        else:
            self.generate()
                
    def show(self):
        self.root.mainloop()