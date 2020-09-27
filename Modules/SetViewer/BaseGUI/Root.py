import tkinter as tk

class RootWidget(tk.Tk):
    """Root widget for complex set viewer.

    Args:
        title (str): Title of the root window.
        dimensions (tuple) (int, int): The (width, height) of the root widget.
        minwidth (int): The minimum width of the root widget.
    
    """
    def __init__(self, title:str, dimensions:tuple, minwidth:int):
        super().__init__()
        self.title = title
        self.dimensions = dimensions
        self.columnconfigure(0, minsize=minwidth)
    
    @property
    def title(self) -> str:
        """str: Title of the root widget. """
        return self._title
    
    @title.setter
    def title(self, title:str):
        self._title = title
        self.wm_title(title)
    
    @property
    def icon(self) -> str:
        """str: Icon filepath of root widget."""
        return self._icon
    
    @icon.setter
    def icon(self, icon:str):
        self._icon = icon
        self.iconbitmap(icon)
    
    @property
    def dimensions(self) -> tuple:
        """tuple: (width, height) Size dimensions of root widget."""
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, dimensions:tuple):
        self._dimensions = dimensions
        self.geometry('%dx%d'%(dimensions[0], dimensions[1]))