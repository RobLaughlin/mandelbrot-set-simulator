import tkinter as tk
from tkinter import ttk
from os import path, makedirs
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as anim
import webbrowser
import copy

from ..ComplexSets.ComplexSet import ComplexSet as Set
from ..ComplexSets.CoordinateRange import CoordinateRange as crange 
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

    def __init__(self, **kwargs):
        self.__init_sets(kwargs['setlist'], kwargs['dimensions'])

        kwargs['coord_range'] = self.selected_set.get_coord_range()
        kwargs['sets'] = self.sets
        super().__init__(**kwargs)
        
        self.maintain_ratio = kwargs['maintain_ratio']
        self.anim = None
        self.after_id = None

    def canvas_onclick(self, event):
        """ Handler for clicking the set canvas """
        
        # Zoom multiplier
        m = 1

        btn_pressed = str(event.button)
        if btn_pressed == 'MouseButton.LEFT':
            m = 0.25
        elif btn_pressed == 'MouseButton.RIGHT':
            m = 3
        
        # Some zoom math
        x_range = self.selected_set.get_coord_range().get_xRange()
        y_range = self.selected_set.get_coord_range().get_yRange()
        x_len = abs(x_range[1] - x_range[0])
        y_len = abs(y_range[1] - y_range[0])
        rel_x = x_range[0] + (x_len) * (event.x / self.width)
        rel_y = y_range[0] + (y_len) * (event.y / self.height)
        pad_x = (m * x_len)
        pad_y = (m * y_len)

        if self.maintain_ratio:
            r = self.canvas.width / self.canvas.height
            pad_x *= r
            pad_y *= r

        pad_x /= 2
        pad_y /= 2

        new_crange = crange(rel_x - pad_x, rel_x + pad_x, rel_y - pad_y, rel_y + pad_y)
        self.sidepanel.components['xy_frame'].update_all(new_crange)
        self.generate_wrapper()

    def animation_checkbox_clicked(self, widget):
        anim_check = self.sidepanel.components['picture'].animation
        anim_check.val = not anim_check.val 
        self.stop_generation(clear=False)
    
    def color_map_changed(self, *args):
        if self.selected_set.get_set() is not None:
            selected_cmap = self.color_map_list.get()
            self.update_canvas(cmap=selected_cmap)
            self.canvas.draw()

    def real_part_changed(self, e):
        selected_set = self.sets[self.set_list.get()]
        real_val = float(self.real_part_slider.get())
        if selected_set.name == 'Julia':
            selected_set.update_constant(real_val + (selected_set.get_constant().imag * 1j))
            self.generate_wrapper()
        
    def imag_part_changed(self, e):
        selected_set = self.sets[self.set_list.get()]
        imag_val = float(self.imag_part_slider.get())
        if selected_set.name == 'Julia':
            selected_set.update_constant(selected_set.get_constant().real + (imag_val * 1j))
            self.generate_wrapper()

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
        
    def stop_generation(self, clear=True):
        # Check if a set is currently being generated
        if self.after_id is not None:
             self.root.after_cancel(self.after_id)
        
        # Stop animation on button click
        if self.anim is not None:
            self.anim.event_source.stop()

        self.update_progress(clear=clear)

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

        selected_set = self.sets[self.set_list.get()]
        coords = self.validate_range_entries()
        maxIters = self.iteration_slider.get()
        selected_set.set_coord_range(coords)
        selected_set.set_iterations(maxIters)
        
        if reset:
            new_set = copy.deepcopy(selected_set)
            self.selected_set = iter(new_set)
        
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

    def pause_btn_clicked(self, widget:tk.Button):
        clear = (self.selected_set.get_current_iteration() >= self.selected_set.get_iterations())
        selected_cmap = self.sidepanel.components['picture'].colormaps.val

        self.stop_generation(clear=clear)
        widget.config(command=lambda: (self.generate_wrapper(reset=False)))
        widget.text = 'Continue'
        self.canvas.update(cmap=selected_cmap)
        
        if self.sidepanel.components['picture'].animation.val == False:
            self.canvas.draw()
    
    def continue_btn_clicked(self, widget:tk.Button):
        pass

    def color_map_changed(self, widget, event):
        pass
    
    def animation_checkbox_clicked(self, widget):
        pass

    def real_part_changed(self, widget):
        pass

    def imag_part_changed(self, widget):
        pass

    def generate_btn_clicked(self, widget):
        pass