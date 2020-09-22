from abc import ABC, abstractclassmethod
import tkinter as tk
from tkinter import ttk
from os import path, makedirs
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import webbrowser

from ...ComplexSets.CoordinateRange import CoordinateRange as crange

class BaseGUI(ABC):
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
    
    def __init__(self, sets, coord_range:crange, dimensions=(600,600), iterations=250, colormap='hot', title='Set Viewer', max_interval_delay=1000):
        colormaps = plt.colormaps()
        if colormap not in colormaps:
            raise BaseGUI.ColorMapNotIncluded('Color map "%s" is not included in the Matplotlib list of color maps.' % colormap)
        
        if dimensions[0] < BaseGUI.MIN_WIDTH:
            raise BaseGUI.MinimumWidthExceeded('BaseGUI width cannot be less than %d pixels.' % BaseGUI.MIN_WIDTH)

        if dimensions[1] < BaseGUI.MIN_HEIGHT:
            raise BaseGUI.MinimumHeightExceeded('BaseGUI height cannot be less than %d pixels.' % BaseGUI.MIN_HEIGHT)

        self.dpi = 100
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.figwidth = self.width / 100
        self.figheight = self.height / 100
        self.figure = plt.figure(figsize=(self.figwidth, self.figheight), dpi=self.dpi)
        """ Ugly monolithic GUI code (most of which is the sidebar) """

        if not path.exists(BaseGUI.SIMULATOR_ICON):
            raise FileNotFoundError('%s File not found.' % BaseGUI.SIMULATOR_ICON)

        # Root widget
        self.root = tk.Tk()
        self.root.wm_title(title)
        self.root.geometry('%dx%d'%(self.width + BaseGUI.SIDEPANEL_WIDTH, self.height))
        self.root.columnconfigure(0, minsize=BaseGUI.SIDEPANEL_WIDTH)
        self.root.iconbitmap(BaseGUI.SIMULATOR_ICON)

        # Main set canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky=tk.E)

        # Left sidepanel frame
        self.sidepanel = tk.LabelFrame(self.root, bd=0)
        self.sidepanel.grid(row=0, column=0, sticky='N')

        # Sidepanel contents
        self.__load_simulation_section(iterations, max_interval_delay, sets)
        self.__load_picture_section(colormaps, colormap)
        self.__load_xyrange_section(coord_range)

        # Close button
        self.close_button = tk.Button(self.sidepanel, text='Close', command=lambda: self.root.quit(), border=2, padx=32, pady=4, width=8)
        self.close_button.grid(row=3, column=0, pady=16, sticky='S')
        
        # Load default set figure
        self.load_default_figure()

        # Github link
        if not path.exists(BaseGUI.GITHUB_PNG):
            raise FileNotFoundError('%s File not found.' % BaseGUI.GITHUB_PNG)

        img = Image.open(BaseGUI.GITHUB_PNG)
        gh_img = ImageTk.PhotoImage(img, master=self.sidepanel)
        self.gh_button = tk.Button(self.sidepanel, image=gh_img, border=1, command=lambda: webbrowser.open(BaseGUI.GITHUB_URL))
        self.gh_button.image = gh_img
        self.gh_button.grid(row=4, column=0, sticky='S')
    
    def __load_simulation_section(self, iterations, max_interval_delay, sets):

        # Simulation frame
        self.simulation_frame = tk.LabelFrame(self.sidepanel, text='Simulation', padx=4, pady=4)
        self.simulation_frame.columnconfigure(0, minsize=BaseGUI.SIDEPANEL_WIDTH - 40)
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
        self.interval_slider = tk.Scale(self.interval_frame, from_=BaseGUI.MIN_FRAME_DELAY, to=max_interval_delay, orient=tk.HORIZONTAL)
        self.interval_slider.set(max_interval_delay // 2)
        self.interval_slider.grid(row=0, column=1)

        # Set list
        self.set_group = tk.LabelFrame(self.simulation_frame, bd=0)
        self.set_list_label = tk.Label(self.set_group, text='Set:')
        self.set_list_label.grid(row=0, column=0, padx=(0, 8))
        self.set_list = ttk.Combobox(self.set_group, values=list(sets.keys()), state='readonly', width=12)
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
        self.picture_frame.columnconfigure(0, minsize=BaseGUI.SIDEPANEL_WIDTH - 40)
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

    def __load_xyrange_section(self, coord_range:crange):

        # XY range frame
        self.xy_frame = tk.LabelFrame(self.sidepanel, text='XY Coordinate Range')
        self.xy_frame.columnconfigure(0, minsize=BaseGUI.SIDEPANEL_WIDTH - 40)
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
        min_x = coord_range.get_xRange()[0]
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
        max_x = coord_range.get_xRange()[1]
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
        min_y = coord_range.get_yRange()[0]
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
        max_y = coord_range.get_yRange()[1]
        self.max_y_entry = tk.Entry(self.max_y_frame, width=8, validate='key', validatecommand=vdbl)
        self.max_y_entry.insert(0, str(max_y))
        self.max_y_entry.grid(row=0, column=1)

    def load_default_figure(self):
        """ Load the null set image into figure when the GUI loads """
        if not path.exists(BaseGUI.NULLSET_PNG):
            raise FileNotFoundError('%s File not found.' % BaseGUI.NULLSET_PNG)
        
        img = Image.open(BaseGUI.NULLSET_PNG)

        # Pad image with emptiness
        new_img = Image.new('RGBA', (self.width, self.height), 'white')
        offset_width = (self.width - img.width) // 2
        offset_height = (self.height - img.height) // 2
        new_img.paste(img, (offset_width, offset_height))
        
        self.figure.figimage(new_img, cmap='gray', origin='lower')

    @abstractclassmethod
    def set_list_changed(self):
        pass

    @abstractclassmethod
    def pause_generation(self):
        pass
    
    @abstractclassmethod
    def color_map_changed(self):
        pass
    
    @abstractclassmethod
    def animation_checkbox_clicked(self):
        pass

    @abstractclassmethod
    def save_button_handler(self):
        pass

    @abstractclassmethod
    def range_entry_handler(self):
        pass

    @abstractclassmethod
    def generate_wrapper(self):
        pass