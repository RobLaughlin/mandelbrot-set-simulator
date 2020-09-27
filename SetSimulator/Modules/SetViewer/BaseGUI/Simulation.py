import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable
from .LabeledWidget import LabeledWidget

class IterationWidget(LabeledWidget):
    """Iteration subcomponent.

    Args:
        master (tkinter.widget): The iteration component's container.
        max_iterations (int): Maximum iterations for complex set calculations.
        grid_index (tuple): (int, int) Location on the tkinter grid system.
        default_value (int, optional): Default value on the iteration scale.

    Attributes:
        max_iterations (int):  Maximum iterations for complex set calculations.
    
    """
    def __init__(self, master:tk.Widget, max_iterations:int, grid_index:tuple, default_value=1):
        widget = tk.Scale
        options = dict({'from_': 1, 'to': max_iterations, 'orient':tk.HORIZONTAL})
        super().__init__(master, (widget, options), 'Iterations:', grid_index)

        self.label.grid_configure(pady=(0, 4), padx=(0, 16))
        self._max_iterations = max_iterations
        self.val = default_value
        
    @property
    def max_iterations(self) -> int:
        """int:  Maximum iterations for complex set calculations."""
        return self._max_iterations

class AnimationDelayWidget(LabeledWidget):
    """Animation delay subcomponent.

    Args:
        master (tkinter.widget): The animation delay component's container.
        max_animation_delay (int): Maximum delay (MS) between franes.
        grid_index (tuple): (int, int) Location on the tkinter grid system.
        default_value (int, optional): Default value on the delay scale.
    
    """
    def __init__(self, master:tk.Widget, max_animation_delay:int, grid_index:tuple, default_value=1):
        widget = tk.Scale
        options = dict({'from_': 1, 'to': max_animation_delay, 'orient':tk.HORIZONTAL})
        super().__init__(master, (widget, options), 'Delay (MS):', grid_index)

        self.label.grid_configure(pady=(0, 4), padx=(0, 8))
        self.val = default_value

class SetListWidget(LabeledWidget):
    """Set list subcomponent.

    Args:
        master (tkinter.widget): The set list component's container.
        handler (function(widget)): Event handler for selecting a different set.
        grid_index (tuple): (int, int) Location on the tkinter grid system.
        default_value (int, optional): Default set

    """
    def __init__(self, master:tk.Widget, handler:Callable, setlist:list, grid_index:tuple, default_value=0):
        widget = ttk.Combobox
        options = dict({'values': setlist, 'state': 'readonly', 'width': 13})
        super().__init__(master, (widget, options), 'Set list:', grid_index)
        self.widget.bind('<<ComboboxSelected>>', lambda event: handler(self))
        self.widget.current(default_value)
        self.label.grid_configure(sticky='W', padx=(0, 26))
        self.grid_configure(pady=8)

class GenerationControlWidget(tk.Frame):
    """Generation control frame subcomponent.

    Args:
        master (tkinter.widget): The generation control component's container.
        generate_handler (function(button)): Event handler for generate button click.
        pause_handler (function(button)): Event handler for pause button click.
        grid_index (tuple): (int, int) Location on the tkinter grid system.
    
    Attributes:
        generate (tkinter.button): Generate set button
        pause (tkinter.button): Pause generation button
    
    """
    def __init__(self, master:tk.Widget, generate_handler:Callable, pause_handler:Callable, continue_handler:Callable, grid_index:tuple):
        super().__init__(master, bd=0)
        self.grid(row=grid_index[0], column=grid_index[1])

        self._pause_handler = pause_handler
        self._continue_handler = continue_handler

        self._generate = tk.Button(self, text='Generate', padx=20, command=lambda: generate_handler(self.generate))
        self._generate.grid(row=0, column=0, pady=8, padx=4)

        self._pause = tk.Button(self, text='Pause', padx=20)
        self.toggle_pause(continue_=False)
        self._pause.grid(row=0, column=1, pady=8, padx=4)
    
    @property
    def generate(self) -> tk.Button:
        """tkinter.button: Generate button"""
        return self._generate

    @property
    def pause(self) -> tk.Button:
        """tkinter.button: Pause button"""
        return self._pause
    
    def toggle_pause(self, continue_:bool):
        """Toggles the pause and continue states for the pause button.

        Args:
            continue_ (bool): Whether to set the pause button to the continue state or the pause state.
        
        """
        if continue_:
            self._pause['text'] = 'Continue'
            self._pause.config(command=lambda: self._continue_handler(self._pause))
        else:
            self._pause['text'] = 'Pause'
            self._pause.config(command=lambda: self._pause_handler(self._pause))

    
 
class SimulationWidget(tk.LabelFrame):
    """Simulation frame subcomponent.

    Args:
        master (tkinter.widget): The simulation frame's container.
        widget_params (dict[str, object]): widget-specific options
        minwidth (int): Minimum width of simulation frame.

    Attributes:
        iterations (simulation.iterationwidget): Iteration widget subcomponent.
        delay (simulation.animationdelaywidget): Frame delay subcomponent.
        setlist (simulation.setlistwidget): Set list subcomponent.
        progress_bar (tkinter.ttk.progressbar): Set generation progress bar subcomponent.
        

    Widget Params:
        max_iterations (int): Maximum iterations for complex set calculations.
        max_delay (int): Maximum animation delay between rendering frames.
        setlist (simulation.setlistwidget): Complex set widget container.
        setlist_changed (function(widget)): Event handler for changing the set list.
        generate_btn_clicked (function(button)): Event handler for clicking the generate button.
        pause_btn_clicked (function(button)): Event handler for clicking the pause button.
    
    """
    def __init__(self, master:tk.Widget, widget_params:Dict[str, object], minwidth:int):
        super().__init__(master=master, padx=4, pady=4, text='Simulation')
        self.columnconfigure(0, minsize=minwidth)

        max_iterations = widget_params['max_iterations']
        max_delay = widget_params['max_delay']
        setlist = widget_params['setlist']
        setlist_changed = widget_params['setlist_changed']
        generate_btn_clicked = widget_params['generate_btn_clicked']
        pause_btn_clicked = widget_params['pause_btn_clicked']
        continue_btn_clicked = widget_params['continue_btn_clicked']

        self._iter_widget = IterationWidget(self, max_iterations, (0, 0), default_value=(max_iterations // 2))
        self._anim_delay_widget = AnimationDelayWidget(self, max_delay, (1, 0), default_value=(max_delay // 2))
        self._set_list_widget = SetListWidget(self, setlist_changed, setlist, (2, 0), default_value=0)
        self._progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode='determinate', length=175)
        self._progress_bar.grid(row=3, column=0, pady=8)
        self._generation = GenerationControlWidget(self, generate_btn_clicked, pause_btn_clicked, continue_btn_clicked, (4, 0))
    
    @property
    def iterations(self) -> IterationWidget:
        """simulation.iterationwidget: Iteration subcomponent."""
        return self._iter_widget
    
    @property
    def delay(self) -> AnimationDelayWidget:
        """simulation.animationdelaywidget: Animation delay subcomponent."""
        return self._anim_delay_widget
    
    @property
    def setlist(self) -> SetListWidget:
        """simulation.animationdelaywidget: Animation delay subcomponent."""
        return self._set_list_widget
    
    @property
    def progress_bar(self) -> ttk.Progressbar:
        """tkinter.ttk.progressbar: Set generation progress bar."""
        return self._progress_bar
    
    @property
    def generation(self) -> GenerationControlWidget:
        """simulation.generationcontrolwidget: Generation control container subcomponent."""
        return self._generation
    