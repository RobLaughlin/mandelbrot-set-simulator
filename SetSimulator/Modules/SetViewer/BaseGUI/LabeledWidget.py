import tkinter as tk
from tkinter import ttk

class LabeledWidget(tk.Frame):
    """Wrapper frame for widgets that have a label and widget side by side.
    
    Args:
        master (tkinter.widget): The LabelWidget's container.
        widget (tuple): (widget, options) The tuple consisting of the widget (tkinter.XX) and its specified options (dict).
        text (str): Text of the label.
        grid_index (tuple): (int, int) Location on the tkinter grid system.

    Attributes:
        widget (tkinter.widget): Widget of the component.
        label (tkinter.label): The label of the component.
        text (str): The label text of the component.
        val (object): The current value of the LabeledWidget.
    
    """
    def __init__(self, master:tk.Widget, widget:tuple, text:str, grid_index:tuple):
        super().__init__(master=master, bd=0)
        self.grid(row=grid_index[0], column=grid_index[1])

        self._label = tk.Label(self, text=text)
        self._label.grid(row=0, column=0, sticky='SW')

        self._widget = widget[0](self)
        self._widget.configure(widget[1])
        self._widget.grid(row=0, column=1)

    @property
    def widget(self) -> tk.Widget:
        """tkinter.widget: The widget of the component."""
        return self._widget

    @property
    def label(self) -> tk.Label:
        """tk.label: The label of the component."""
        return self._label
    
    @property
    def text(self) -> str:
        """str: The label text of the component."""
        return self._label.get()
    
    @property
    def val(self) -> object:
        """object: The current value of the component widget."""
        return self._widget.get()
    
    @val.setter
    def val(self, value:object):
        if isinstance(self._widget, tk.Entry):
            self._widget.delete(0, tk.END)
            self._widget.insert(0, str(value))
        
        if type(self._widget) is not tk.Entry:
            self._widget.set(value)