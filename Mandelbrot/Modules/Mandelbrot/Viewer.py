from .CoordinateRange import CoordinateRange
from .Mandelbrot import Mandelbrot
from matplotlib import pyplot as plt

class MandelbrotViewer(Mandelbrot):
    def __init__(self, iterations:int, coord_range:CoordinateRange, figsize=(8,8), dpi=100):
        """
        GUI inherited class of the Mandelbrot set. 
        Displays the Mandelbrot set visually using pyplot.

        Params in addition to the Mandelbrot class:
        figsize (x, y) - Size of the figure in inches
        dpi - pixels per inch

        ex: figsize=(8,8) dpi=100 yields a 800x800 pixel figure.
        """

        super().__init__(iterations=iterations, coord_range=coord_range)
        self.figsize = figsize
        self.dpi = dpi

        plt.figure(figsize=figsize, dpi=dpi)

    def show(self, colormap='gray', aspect_ratio='auto'):
        if self.set_template is None:
            self.generate_template(int(self.figsize[0] * self.dpi), int(self.figsize[1] * self.dpi))
            
        if self.set is None:
            self.generate_set()
        
        plt.imshow(self.set['divergence'], cmap=colormap, aspect=aspect_ratio)
        plt.show()
