import tkinter as tk
from tkinter import ttk
from os import path, makedirs
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
import json
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as anim
import webbrowser
import math
import time
import copy

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
    
    GITHUB_URL = 'https://github.com/RobLaughlin/complex-set-simulator'

    NULLSET_PNG = 'img/nullset.png'
    GITHUB_PNG = 'img/github.png'
    SIMULATOR_ICON = 'img/mset.ico'
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
                if s.get_template() is None:
                    s.generate_template(self.width, self.height)

                sets[s.name] = s
        
        self.sets = sets
        self.selected_set = iter(copy.deepcopy(setlist[0]))

    def __init__(self, setlist, dimensions=(600,600), iterations=250, colormap='hot', title='Set Viewer', max_interval_delay=1000):
        colormaps = plt.colormaps()
        if colormap not in colormaps:
            raise SetViewer.ColorMapNotIncluded('Color map "%s" is not included in the Matplotlib list of color maps.'%colormap)
        
        if dimensions[0] < SetViewer.MIN_WIDTH:
            raise SetViewer.MinimumWidthExceeded('SetViewer width cannot be less than %d pixels.' % SetViewer.MIN_WIDTH)

        if dimensions[1] < SetViewer.MIN_HEIGHT:
            raise SetViewer.MinimumHeightExceeded('SetViewer height cannot be less than %d pixels.' % SetViewer.MIN_HEIGHT)

        self.dpi = 100
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.figwidth = self.width / 100
        self.figheight = self.height / 100
        self.figure = plt.figure(figsize=(self.figwidth, self.figheight), dpi=self.dpi)

        self.__init_sets(setlist)

        # For depth of zoom on canvas
        self.zoom_level = 0

        # Animation source for the set being generated
        self.anim = None

        # To track where tkinter is during the generation process
        self.after_id = None

        self.__init_GUI(iterations, colormap, title, max_interval_delay, colormaps)

    def __init_GUI(self, iterations, colormap, title, max_interval_delay, colormaps):
        """ Ugly monolithic GUI code (most of which is the sidebar) """

        if not path.exists(SetViewer.SIMULATOR_ICON):
            raise FileNotFoundError('%s File not found.' % SetViewer.SIMULATOR_ICON)

        # Root widget
        self.root = tk.Tk()
        self.root.wm_title(title)
        self.root.geometry('%dx%d'%(self.width + SetViewer.SIDEPANEL_WIDTH, self.height))
        self.root.columnconfigure(0, minsize=SetViewer.SIDEPANEL_WIDTH)
        self.root.iconbitmap(SetViewer.SIMULATOR_ICON)

        # Main set canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky=tk.E)

        # Left sidepanel frame
        self.sidepanel = tk.LabelFrame(self.root, bd=0)
        self.sidepanel.grid(row=0, column=0, sticky='N')

        # Sidepanel contents
        self.__load_simulation_section(iterations, max_interval_delay)
        self.__load_picture_section(colormaps, colormap)
        self.__load_xyrange_section()

        # Close button
        self.close_button = tk.Button(self.sidepanel, text='Close', command=lambda: self.root.quit(), border=2, padx=32, pady=4, width=8)
        self.close_button.grid(row=3, column=0, pady=16, sticky='S')
        
        # Load default set figure
        self.load_default_figure()

        # Github link
        if not path.exists(SetViewer.GITHUB_PNG):
            raise FileNotFoundError('%s File not found.' % SetViewer.GITHUB_PNG)

        img = Image.open(SetViewer.GITHUB_PNG)
        gh_img = ImageTk.PhotoImage(img, master=self.sidepanel)
        self.gh_button = tk.Button(self.sidepanel, image=gh_img, border=1, command=lambda: webbrowser.open(SetViewer.GITHUB_URL))
        self.gh_button.image = gh_img
        self.gh_button.grid(row=4, column=0, sticky='S')

        # Set zoom handler
        self.canvas.mpl_connect('button_press_event', self.canvas_onclick)
    
    def __load_simulation_section(self, iterations, max_interval_delay):

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
        self.set_list.bind("<<ComboboxSelected>>", self.set_list_changed)
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
        self.generate_button = tk.Button(self.generation_frame, text='Generate', padx=20, command=self.generate_wrapper)
        self.generate_button.grid(row=0, column=0, pady=8, padx=4)

        # Pause generation button
        self.pause_button = tk.Button(self.generation_frame, padx=20, command=self.pause_generation, text='Pause')
        self.pause_button['state'] = 'disabled'
        self.pause_button.grid(row=0, column=1, pady=8, padx=4)

    def __load_picture_section(self, colormaps, colormap):

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
        self.animation_check_val = tk.BooleanVar(value=True)
        self.animation_checkbox = tk.Checkbutton(self.picture_frame, text='Animation', 
                                                variable=self.animation_check_val, command=self.animation_checkbox_clicked)
        self.animation_checkbox.grid(row=1, column=0, padx=(0, 8), pady=2, sticky='W')
        self.animation_checkbox.select()

        # Save button
        self.save_button = tk.Button(self.picture_frame, text='Save Image', command=self.save_button_handler, padx=32, pady=4, width=8)
        self.save_button.grid(row=3, column=0, pady=8)

    def __load_xyrange_section(self):

        # XY range frame
        self.xy_frame = tk.LabelFrame(self.sidepanel, text='XY Coordinate Range')
        self.xy_frame.columnconfigure(0, minsize=SetViewer.SIDEPANEL_WIDTH - 40)
        self.xy_frame.grid(row=2, column=0)
        
        # Validate entry command
        vdbl = (self.root.register(self.range_entry_handler), '%S', '%P')

        # X range frame
        self.x_frame = tk.LabelFrame(self.xy_frame, bd=0)
        self.x_frame.grid(row=0, column=0, pady=(8, 0))

        # Min x frame
        self.min_x_frame = tk.LabelFrame(self.x_frame, bd=0)
        self.min_x_frame.grid(row=0, column=0, padx=4)
        
        # Min x label
        self.min_x_label = tk.Label(self.min_x_frame, text='Min x:')
        self.min_x_label.grid(row=0, column=0)

        # Min x entry
        min_x = self.selected_set.get_coord_range().get_xRange()[0]
        self.min_x_entry = tk.Entry(self.min_x_frame, width=8, validate='key', validatecommand=vdbl)
        self.min_x_entry.insert(0, str(min_x))
        self.min_x_entry.grid(row=0, column=1)

        # Max x frame
        self.max_x_frame = tk.LabelFrame(self.x_frame, bd=0)
        self.max_x_frame.grid(row=0, column=1, padx=4)

        # Max x label
        self.max_x_label = tk.Label(self.max_x_frame, text='Max x:')
        self.max_x_label.grid(row=0, column=0)

        # Max x entry
        max_x = self.selected_set.get_coord_range().get_xRange()[1]
        self.max_x_entry = tk.Entry(self.max_x_frame, width=8, validate='key', validatecommand=vdbl)
        self.max_x_entry.insert(0, str(max_x))
        self.max_x_entry.grid(row=0, column=1)

        # Y range frame
        self.y_frame = tk.LabelFrame(self.xy_frame, bd=0)
        self.y_frame.grid(row=1, column=0, pady=8)

        # Min y frame
        self.min_y_frame = tk.LabelFrame(self.y_frame, bd=0)
        self.min_y_frame.grid(row=0, column=0, padx=4)
        
        # Min y label
        self.min_y_label = tk.Label(self.min_y_frame, text='Min y:')
        self.min_y_label.grid(row=0, column=0)

        # Min y entry
        min_y = self.selected_set.get_coord_range().get_yRange()[0]
        self.min_y_entry = tk.Entry(self.min_y_frame, width=8, validate='key', validatecommand=vdbl)
        self.min_y_entry.insert(0, str(min_y))
        self.min_y_entry.grid(row=0, column=1)

        # Max y frame
        self.max_y_frame = tk.LabelFrame(self.y_frame, bd=0)
        self.max_y_frame.grid(row=0, column=1, padx=4)

        # Max y label
        self.max_y_label = tk.Label(self.max_y_frame, text='Max y:')
        self.max_y_label.grid(row=0, column=0)

        # Max y entry
        max_y = self.selected_set.get_coord_range().get_yRange()[1]
        self.max_y_entry = tk.Entry(self.max_y_frame, width=8, validate='key', validatecommand=vdbl)
        self.max_y_entry.insert(0, str(max_y))
        self.max_y_entry.grid(row=0, column=1)

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
    
    def load_default_figure(self):
        """ Load the null set image into figure when the GUI loads """
        if not path.exists(SetViewer.NULLSET_PNG):
            raise FileNotFoundError('%s File not found.' % SetViewer.NULLSET_PNG)
        
        img = Image.open(SetViewer.NULLSET_PNG)

        # Pad image with emptiness
        new_img = Image.new('RGBA', (self.width, self.height), 'white')
        offset_width = (self.width - img.width) // 2
        offset_height = (self.height - img.height) // 2
        new_img.paste(img, (offset_width, offset_height))
        
        self.figure.figimage(new_img, cmap='gray', origin='lower')
        
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