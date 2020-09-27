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
    GUI Controller/SetViewer for sets.

    Args:
        setlist (list): List of complex set objects.
        title (str): Title of the window.
        colormap (str): Default colormap to apply to the GUI figure.
        iterations (int): Max number of iterations to simulate.
        dimensions (tuple) (int, int): used to initialize respective width and height of the root widget.
        max_interval_delay (int): Max delay between frame animation.
        julia_constant (complex) (real, imag):  specific constant to use for simulating the Julia set.
        maintain_ratio (bool): Whether to attempt maintaining the aspect ratio when initialized.
    
    Attributes:
        sets (dict[str, complexset]): Dictionary of complex set objects, key being the name of the set.
        selected_set (complexset): The selected set to be generated.
        maintain_ratio (bool): Whether to attempt maintaining the aspect ratio when initialized.
        simulation (tkinter.widget): The simulation subcomponent in the sidepanel.
        picture (tkinter.widget): The picture subcomponent in the sidepanel.
        xy_frame (tkinter.widget): The xy frame subcomponent in the sidepanel.
        julia_constant (tkinter.widget): The Julia constant subcomponent in the sidepanel.
        anim (function): The render function for the set generation animation.
        after_id (str): The string ID to keep track of animation.

    """

    def __init_sets(self, setlist:list, dimensions:tuple):
        """Initialization for each set in the set list by generating their respective templates.
        
        Args:
            setlist (list): List of complex set objects.
            dimensions (tuple) (int, int): Used to generate a template with respect to the canvas' (width, height).
        
        Raises:
            IndexError: If the set list is empty.
        
        """
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
    
    def __generate(self):
        """Complex set generation helper function."""
        try:
            delay = self.simulation.delay.val
            next(self.selected_set)
            self.update_progress()
            self.after_id = self.root.after(self.simulation.delay.val, self.__generate)
        except StopIteration:
            self.stop_generation()
            self.canvas.update(self.selected_set.get_set()['divergence'], cmap=self.picture.colormaps.val, redraw=True)
            self.simulation.generation.pause['state'] = 'disabled'
            self.simulation.generation.toggle_pause(continue_=False)

    def __render(self):
        """Callback for every frame in animation."""
        if self.picture.animation.val:
            self.anim.event_source.interval = self.simulation.delay.val

            try:
                next(self.selected_set)
                self.canvas.update(self.selected_set.get_set()['divergence'], cmap=self.picture.colormaps.val)
                self.update_progress()
            except StopIteration:
                self.canvas.update(self.selected_set.get_set()['divergence'], cmap=self.picture.colormaps.val, redraw=True)
                self.stop_generation()
                self.simulation.generation.pause['state'] = 'disabled'
                self.simulation.generation.toggle_pause(continue_=False)
        else:
            self.anim.event_source.stop()

    def __init__(self, **kwargs):
        self.__init_sets(kwargs['setlist'], kwargs['dimensions'])

        kwargs['coord_range'] = self.selected_set.get_coord_range()
        kwargs['sets'] = self.sets
        super().__init__(**kwargs)

        self.simulation = self.sidepanel.components['simulation']
        self.picture = self.sidepanel.components['picture']
        self.xy_frame = self.sidepanel.components['xy_range']
        self.julia_constant = self.sidepanel.components['julia_constant']

        self.maintain_ratio = kwargs['maintain_ratio']
        self.anim = None
        self.after_id = None

    def stop_generation(self, clear=True):
        """Stop the iterative generation of the current set being generated.
        
        Args:
            clear (bool, optional): Whether to clear the progress bar after stopping the generation.
        
        """
        # Check if a set is currently being generated
        if self.after_id is not None:
             self.root.after_cancel(self.after_id)
        
        # Stop animation on button click
        if self.anim is not None:
            self.anim.event_source.stop()

        self.update_progress(clear=clear)

    def update_progress(self, clear=False):
        """Update the progress bar value.

        Args:
            clear (bool, optional): Whether to clear the progress bar after stopping the generation.
        
        """
        if clear:
            self.simulation.progress_bar['value'] = 0
        else:
            self.simulation.progress_bar['value'] = (self.selected_set.get_current_iteration() / self.selected_set.get_iterations()) * 100

        self.root.update_idletasks()
            
    def generate(self, reset=True):
        """Main initial generation function for generating complex sets.
        
        Args:
            reset (bool, optional): Whether to reset the progress already generated, ex: set to False if generation is paused.
        
        Returns:
            coordinaterange.exception: If there was an error setting the coordinate range of the set.
            None: If generation succeeded.
         
        """
        self.simulation.generation.pause['state'] = 'active'
        self.simulation.generation.toggle_pause(continue_=False)
        self.stop_generation()

        selected_set = self.sets[self.simulation.setlist.val]
        coords = self.xy_frame.coord_range
        maxIters = self.simulation.iterations.val

        if isinstance(coords, Exception):
            tk.messagebox.showerror(title='Error', message=coords)
            return coords
        
        selected_set.set_coord_range(coords)
        selected_set.set_iterations(maxIters)
        
        if reset:
            new_set = copy.deepcopy(selected_set)
            self.selected_set = iter(new_set)
        
        # Check for animation enabled
        if self.picture.animation.val:
            delay = self.simulation.delay.val
            self.anim = anim.FuncAnimation(self.canvas.figure, lambda frame: self.__render(), interval=delay, 
                                            repeat=False, blit=False, cache_frame_data=False)
            self.canvas.draw()
        else:
            self.__generate()

    def show(self):
        """Show the GUI."""
        self.root.mainloop()

    def canvas_onclick(self, widget:tk.Widget, event):
        """Handler for clicking the canvas. Current implementation is left click for zoom in and right click for zoom out.
        
        Args:
            widget (tkinter.widget): The widget that was clicked (canvas).
            event (matplotlib.backend_bases.mouseevent): Event data regarding where on the canvas was clicked.
        
        """
        
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
        rel_x = x_range[0] + (x_len) * (event.x / self.canvas.width)
        rel_y = y_range[0] + (y_len) * (event.y / self.canvas.height)
        pad_x = (m * x_len)
        pad_y = (m * y_len)

        if self.maintain_ratio:
            r = self.canvas.width / self.canvas.height
            pad_x *= r
            pad_y *= r

        pad_x /= 2
        pad_y /= 2

        new_crange = crange(rel_x - pad_x, rel_x + pad_x, rel_y - pad_y, rel_y + pad_y)
        self.xy_frame.update_all(new_crange)
        self.generate()

    def pause_btn_clicked(self, widget:tk.Button):
        """Handler for clicking the pause button.
        
        Args:
            widget (tkinter.button): The button that was clicked (pause button).
        
        """
        clear = (self.selected_set.get_current_iteration() >= self.selected_set.get_iterations())

        self.stop_generation(clear=clear)
        self.simulation.generation.toggle_pause(continue_=True)
        self.canvas.update(self.selected_set.get_set()['divergence'], cmap=self.picture.colormaps.val)
        
        if not self.picture.animation.val:
            self.canvas.draw()
    
    def continue_btn_clicked(self, widget:tk.Button):
        """Handler for clicking the continue button.
        
        Args:
            widget (tkinter.button): The button that was clicked (continue button).
        
        """
        self.generate(reset=False)

    def color_map_changed(self, widget:tk.Widget):
        """Handler for when a different colormap has been selected.
        
        Args:
            widget (tkinter.widget): The colormap container.
        
        """
        if self.selected_set.get_set() is not None:
            self.canvas.update(self.selected_set.get_set()['divergence'], cmap=widget.val, redraw=True)

    def animation_checkbox_clicked(self, widget:tk.Widget):
        """Handler for when the animation checkbox has been ticked or unticked.
        
        Args:
            widget (tkinter.widget): The animation checkbox container.
        
        """
        anim_check = self.picture.animation
        anim_check.val = not anim_check.val
        self.stop_generation(clear=False)

    def real_part_changed(self, widget:tk.Widget):
        """Handler for when the value of the real part widget has been changed.
        
        Args:
            widget (tkinter.widget): The real part container widget.
        
        """
        selected_set = self.sets[self.simulation.setlist.val]
        real_val = self.julia_constant.real
        if selected_set.name == 'Julia':
            selected_set.update_constant(real_val + (selected_set.get_constant().imag * 1j))
            self.generate()
        
    def imag_part_changed(self, widget:tk.Widget):
        """Handler for when the value of the imaginary part widget has been changed.
        
        Args:
            widget (tkinter.widget): The imaginary part container widget.
        
        """
        selected_set = self.sets[self.simulation.setlist.val]
        imag_val = self.julia_constant.imag
        if selected_set.name == 'Julia':
            selected_set.update_constant(selected_set.get_constant().real + (imag_val * 1j))
            self.generate()

    def generate_btn_clicked(self, widget:tk.Button):
        """Onclick event for the generation button.
        
        Args:
            widget (tkinter.button): The generation button.
        
        """
        self.generate()