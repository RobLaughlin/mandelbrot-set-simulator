import tkinter as tk
from typing import Dict

class SidepanelWidget(tk.Frame):
    """Sidepanel container for complex set viewer.

    Args:
        master (widget): Container of Sidepanel widget.
        grid_index (tuple): (row, column) Position on grid.
    
    Attributes:
        row (int): Latest grid row of sidepanel subcomponent.
        components (Dict[str, widget]): Dict of subcomponents in the sidepanel.
    
    """

    def __init__(self, master:tk.Widget, grid_index:tuple):
        super().__init__(master=master)
        self._row = 0
        self.grid_configure(row=grid_index[0], column=grid_index[1])
        self._subcomponents = dict()

    @property
    def row(self):
        """int: Row of subcomponent in Sidepanel."""
        return self._row
    
    @property
    def components(self) -> Dict[str, tk.Widget]:
        """Dict[str, widget]: Dict of subcomponents in sidepanel."""
        return self._subcomponents

    def add_component(self, key:str, component:tk.Widget):
        """Add subcomponent to the sidepanel.
        
        Args:
            component (widget): The component to add to the sidepanel
            key (str): Identifier of specified subcomponent
        
        """

        self._row += 1
        self._subcomponents[key] = component
        self._subcomponents[key].grid(row=self._row, column=0)