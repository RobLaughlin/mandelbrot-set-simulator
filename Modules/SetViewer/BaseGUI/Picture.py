import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable
from .LabeledWidget import LabeledWidget

class AnimationCheckbox(tk.Checkbutton):
    """Animation checkbox subcomponent.

    Args:
        master (tkinter.widget): Animation checkbox container widget.
        handler (function(widget)): Event handler for checkbox click.
        grid_index (tuple) (int, int): (Row, Col) position on the tkinter grid.
        checked_default (bool): Whether to initially check the animation checkbox.
    
    Attributes:
        val (bool): Value of the animation checkbox.
    
    """
    def __init__(self, master:tk.Widget, handler:Callable, grid_index:tuple, checked_default=True):
        self._val = tk.BooleanVar(value=checked_default)
        super().__init__(master, text='Animation', command=lambda: handler(self), variable=self._val)
        self.select() if checked_default else self.deselect()
        self.grid(row=grid_index[0], column=grid_index[1], sticky='W', padx=(16, 0))

    @property
    def val(self) -> bool:
        """tkinter.booleanvar: Value of animation checkbox."""
        return self._val.get()

    @val.setter
    def val(self, value:bool):
        self._val.set(value=value)
        self.select() if value else self.deselect()

class ColormapWidget(LabeledWidget):
    """Colormap subcomponent.

    Args:
        master (tkinter.widget): Colormap container widget.
        handler (function(widget)): Event handler for widget selection
        grid_index (tuple) (int, int): (Row, Col) position on the tkinter grid.
        colormaps (list): List of available Matplotlib colormaps.
        default_value (str): Default colormap.
    
    """
    def __init__(self, master:tk.Widget, handler:Callable, grid_index:tuple, colormaps:list, default_value:str):
        widget = ttk.Combobox
        options = {'values': colormaps, 'state': 'readonly', 'width': 13}
        super().__init__(master, (widget, options), 'Color map:', grid_index)

        self.grid_configure(pady=4)
        self.label.grid_configure(padx=(0, 8))
        self.val = default_value
        self.widget.bind("<<ComboboxSelected>>", lambda event: handler(self))
    
class PictureWidget(tk.LabelFrame):
    """Picture (GUI) frame.

    Args:
        master (tkinter.widget): Container widget for picture frame.
        widget_params (dict[str, object]): widget-specific options.
        minwidth (int): Minimum width of picture frame.
    
    Attributes:
        colormaps (picture.colormapwidget): Color map container widget.
        animation (picture.animationcheckbox): Checkbox for enabling/disabling animation.
        save_button (tkinter.button): Save image button.
    
    Widget Args:
        colormaps (list): List of available Matplotlib color maps.
        default_colormap (str): Default color map to select on load.
        colormap_changed (function(widget)): Event handler for colormap changing selection.
        anim_btn_clicked (function(widget)): Event handler for clicking the animation button.
        save_btn_clicked (function(widget)): Event handler for clicking the save button.
    
    """
    def __init__(self, master:tk.Widget, widget_params:Dict[str, object], minwidth:int):
        super().__init__(master, text='Picture')
        self.columnconfigure(0, minsize=minwidth)

        colormaps = widget_params['colormaps']
        default_colormap = widget_params['default_colormap']
        colormap_changed = widget_params['colormap_changed']
        animation_button_clicked = widget_params['anim_btn_clicked']
        save_button_handler = widget_params['save_btn_clicked']

        self._colormaps = ColormapWidget(self, colormap_changed, (0, 0), colormaps, default_colormap)
        self._animation_widget = AnimationCheckbox(self, animation_button_clicked, (1, 0), True)
        self._save_button = tk.Button(self, text='Save Image', command=lambda: save_button_handler(self._save_button), padx=32, width=8)
        self._save_button.grid(row=2, column=0, pady=8)
    
    @property
    def colormaps(self) -> ColormapWidget:
        """picture.colormapwidget: Available Matplotlib color maps."""
        return self._colormaps
    
    @property
    def animation(self) -> AnimationCheckbox:
        """picture.animationcheckbox: Animation checkbox."""
        return self._animation_widget
    
    @property
    def save_button(self) -> tk.Button:
        """tkinter.button: Save image button."""
        return self._save_button