from abc import ABC, abstractclassmethod
import tkinter as tk
from tkinter import ttk
from os import path, makedirs
from matplotlib import pyplot as plt
from PIL import Image, ImageTk
import webbrowser
import time

from ...ComplexSets.CoordinateRange import CoordinateRange as crange
from .Root import RootWidget as Root
from .Sidepanel import SidepanelWidget as Sidepanel
from .Simulation import SimulationWidget as SimulationSection
from .Picture import PictureWidget as Picture
from .XYFrame import XYFrame
from .JuliaConstantWidget import JuliaConstantWidget as JuliaConstant
from .CanvasContainer import Canvas

class MinimumWidthExceeded(Exception):
    """Minimum width of the GUI does not match the static minimum width."""
    pass

class MinimumHeightExceeded(Exception):
    """Minimum height of the GUI does not match the static minimum height."""
    pass

class ColorMapNotIncluded(Exception):
    """Color map is not included in the color maps provided by Matplotlib."""
    pass

class BaseGUI(ABC):
    """Initialize the base GUI for the set simulator.

    Args:
        sets (dict[str, ComplexSets]): Mapping of set names to Complex Set objects.
        title (str): Title of the window.
        colormap (str): Default colormap to apply to the GUI figure.
        iterations (int): Max number of iterations to simulate.
        dimensions (tuple) (int, int): used to initialize the respective (width, height) of root widget.
        max_interval_delay (int): Max delay between frame animation.
        julia_constant (complex): (real, imag) specific constant to use for simulating the Julia set.
        coord_range (coordinaterange): the default coordinate range initialized in the GUI.
    
    Attributes:
        GITHUB_URL (str): GitHub URI.
        GITHUB_PNG (str): GitHub logo/icon path.
        DEFAULT_PNG (str): Default image path to use for figure before set generation.
        SIMULATOR_ICON (str): Icon path for GUI.
        SAVE_DIRECTORY (str): Directory path where images will be saved.
        MIN_WIDTH (int): Minimum width of the GUI in pixels.
        MIN_HEIGHT (int): Minimum height of the GUI in pixels.
        SIDEPANEL_WIDTH (int): Width of the GUI Sidepanel.

        width (int): Width of the GUI.
        height (int): Height of the GUI.
        figure (matplotlib.pyplot.figure): Figure to display the generated sets.
        canvas (matplotlib.backends.backend_tkagg.figurecanvastkagg): Canvas to connect matplotlib figure and tkinter.
        root (RootWidget): Top-level widget for GUI
        sidepanel (SidepanelWidget): Main sidepanel container for most of the GUI controls.
        
    Raises:
        MinimumWidthExceeded: Minimum width of the GUI does not match the static minimum width.
        MinimumHeightExceeded: Minimum height of the GUI does not match the static minimum height.
        ColorMapNotIncluded: Color map is not included in the color maps provided by Matplotlib.
        FileNotFoundError: Static images/files were not found in the img/ filepath.

    """

    GITHUB_URL = 'https://github.com/RobLaughlin/complex-set-simulator'
    GITHUB_PNG = 'img/github.png'
    DEFAULT_PNG = 'img/nullset.png'
    SIMULATOR_ICON = 'img/mset.ico'
    SAVE_DIRECTORY = 'images'
    MIN_WIDTH = 650
    MIN_HEIGHT = 650
    SIDEPANEL_WIDTH = 250
    
    def __init__(self, **kwargs):
        colormaps = plt.colormaps()
        if kwargs['colormap'] not in colormaps:
            raise ColorMapNotIncluded('Color map "%s" is not included in the Matplotlib list of color maps.' % kwargs['colormap'])
        
        if kwargs['dimensions'][0] < BaseGUI.MIN_WIDTH:
            raise MinimumWidthExceeded('BaseGUI width cannot be less than %d pixels.' % BaseGUI.MIN_WIDTH)

        if kwargs['dimensions'][1] < BaseGUI.MIN_HEIGHT:
            raise MinimumHeightExceeded('BaseGUI height cannot be less than %d pixels.' % BaseGUI.MIN_HEIGHT)

        if not path.exists(BaseGUI.SIMULATOR_ICON):
            raise FileNotFoundError('%s File not found.' % BaseGUI.SIMULATOR_ICON)

        if not path.exists(BaseGUI.GITHUB_PNG):
            raise FileNotFoundError('%s File not found.' % BaseGUI.GITHUB_PNG)

        minwidth = BaseGUI.SIDEPANEL_WIDTH - 40
        dims = kwargs['dimensions']
        new_dims = (dims[0] + BaseGUI.SIDEPANEL_WIDTH, dims[1])

        # Width/Height specifications
        self.width = new_dims[0]
        self.height = new_dims[1]
        self.figure = plt.figure(figsize=(dims[0] / 100, dims[1] / 100), dpi=100)

        # Main GUI components
        self.root = Root(kwargs['title'], new_dims, minwidth=BaseGUI.SIDEPANEL_WIDTH)
        self.root.icon = BaseGUI.SIMULATOR_ICON
        self.canvas = Canvas(self.root, self.canvas_onclick, (dims[0], dims[1]), BaseGUI.DEFAULT_PNG, 100)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky='E')

        # Validation function for coordinate range entries
        validate = (self.root.register(self.range_entry_handler), '%S', '%P')

        #Sidepanel subcomponent configuration
        simulation_widget_config = {'max_iterations': kwargs['iterations'],
                                    'max_delay': kwargs['max_interval_delay'],
                                    'setlist': list(kwargs['sets'].keys()),
                                    'setlist_changed' : self.set_list_changed,
                                    'generate_btn_clicked': self.generate_btn_clicked,
                                    'pause_btn_clicked': self.pause_btn_clicked,
                                    'continue_btn_clicked': self.continue_btn_clicked}

        picture_widget_config = {'colormaps': colormaps,
                                'default_colormap': kwargs['colormap'],
                                'colormap_changed': self.color_map_changed,
                                'anim_btn_clicked': self.animation_checkbox_clicked,
                                'save_btn_clicked': self.save_btn_clicked}

        xy_widget_config = {'coord_range': kwargs['coord_range'],
                            'validate': validate}
        
        julia_constant_config = {'real_handler': self.real_part_changed,
                                'real_range': (-2, 2),
                                'imag_handler': self.imag_part_changed,
                                'imag_range': (-2, 2),
                                'default_value': kwargs['julia_constant']}

        self.sidepanel = Sidepanel(self.root, (0, 0))
        self.sidepanel.grid_configure(sticky='N')

        #Sidepanel components/subcomponents
        simulation = SimulationSection(self.sidepanel, simulation_widget_config, minwidth)
        picture = Picture(self.sidepanel, picture_widget_config, minwidth)        
        xy_frame = XYFrame(self.sidepanel, xy_widget_config, minwidth)
        julia_constant = JuliaConstant(self.sidepanel, julia_constant_config, minwidth)
        
        close_button = tk.Button(self.sidepanel, text='Close', command=self.root.quit, border=2, padx=32, pady=4, width=8)
        close_button.grid(pady=8, sticky='S')

        gh_img = ImageTk.PhotoImage(Image.open(BaseGUI.GITHUB_PNG), master=self.sidepanel)
        gh_button = tk.Button(self.sidepanel, image=gh_img, border=1, command=lambda: webbrowser.open(BaseGUI.GITHUB_URL))
        gh_button.image = gh_img
        gh_button.grid(sticky='S')

        self.sidepanel.add_component('simulation', simulation)
        self.sidepanel.add_component('picture', picture)
        self.sidepanel.add_component('xy_range', xy_frame)
        self.sidepanel.add_component('julia_constant', julia_constant)
        self.sidepanel.add_component('close', close_button)
        self.sidepanel.add_component('github', gh_button)

        if simulation.setlist.val != 'Julia':
            julia_constant.hide()
    
    def set_list_changed(self, widget:tk.Widget):
        """Event handler for when a different set is selected from the set list.
        
        Args:
            widget (tkinter.widget): The set list container widget.
        
        """
        self.root.focus()
        julia_constant = self.sidepanel.components['julia_constant']
        julia_constant.show() if widget.val == 'Julia' else julia_constant.hide()

    def save_btn_clicked(self, widget:tk.Button):
        """Event handler for save button click.
        
        Args:
            widget (tkinter.button): The save button.
        
        """
        if not path.exists(BaseGUI.SAVE_DIRECTORY):
            makedirs(BaseGUI.SAVE_DIRECTORY)
        
        current_time = time.strftime("%Y-%m-%d %I %M %p")
        plt.savefig(BaseGUI.SAVE_DIRECTORY + '/%s Set - %s' % (self.sidepanel.components['simulation'].setlist.val, current_time))
    
    def range_entry_handler(self, key, entry):
        """Validation function for each keystroke of a XY range entry.

        Args:
            key (str): What specific key was entered into the XY field.
            entry (str): The full entry value of the XY field. 
        
        Returns:
            bool: True if validation succeeds, False otherwise.
        
        """
        try:
            float(entry)
        except:
            if entry != '':
                return False
        
        return True

    @abstractclassmethod
    def pause_btn_clicked(self, widget:tk.Widget):
        """Event handler for pause button onclick. Overridden by implementation.
        
        Args:
            widget (tkinter.widget): Widget container of what component triggered the event.
        
        """
        pass
    
    @abstractclassmethod
    def continue_btn_clicked(self, widget:tk.Button):
        """Event handler for continue button onclick. Overridden by implementation.
        
        Args:
            widget (tkinter.button): The button that triggered the onclick event.
        
        """
        pass

    @abstractclassmethod
    def color_map_changed(self, widget:tk.Widget):
        """Event handler for selected colormap change. Overridden by implementation.
        
        Args:
            widget (tkinter.widget): Widget container of what component triggered the event.
        
        """
        pass
    
    @abstractclassmethod
    def animation_checkbox_clicked(self, widget:tk.Widget):
        """Event handler for animation checkbox onclick. Overridden by implementation.
        
        Args:
            widget (tkinter.widget): Widget container of what component triggered the event.
        
        """
        pass

    @abstractclassmethod
    def real_part_changed(self, widget:tk.Widget):
        """Event handler for the real part widget change. Overridden by implementation.
        
        Args:
            widget (tkinter.widget): Widget container of what component triggered the event.
        
        """
        pass

    @abstractclassmethod
    def imag_part_changed(self, widget:tk.Widget):
        """Event handler for the real part widget change. Overridden by implementation.
        
        Args:
            widget (tkinter.widget): Widget container of what component triggered the event.
        
        """
        pass

    @abstractclassmethod
    def generate_btn_clicked(self, widget:tk.Button):
        """Event handler for the generation button onclick. Overridden by implementation.
        
        Args:
            widget (tkinter.button): The generation button.
        
        """
        pass

    @abstractclassmethod
    def canvas_onclick(self, widget:tk.Widget, event):
        """Event handler for the canvas onclick. Overridden by implementation.
        
        Args:
            widget (tkinter.widget): Widget container of what component triggered the event.
            event (matplotlib.backend_bases.mouseevent): Event data regarding where on the canvas was clicked.
        
        """
        pass