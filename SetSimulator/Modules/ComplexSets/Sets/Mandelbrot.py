from ..ComplexSet import ComplexSet
from ..CoordinateRange import CoordinateRange
import numpy as np

class Mandelbrot(ComplexSet):
    """Generates a best estimate of the Mandelbrot Set given a limit placed on recursion iterations.

    Args:
        iterations (int): The maximum number of iterations for Mandelbrot set generation.
        coord_range (coordinaterange) ((float, float), (float, float)): X and Y range values, respectively.
        xy_vals (tuple) (int, int): How many intervals to split the x and y axis into.
    
    """
    
    def __init__(self, iterations:int, coord_range:CoordinateRange, xy_vals:tuple):
        super().__init__(iterations, coord_range, xy_vals, 'Mandelbrot')
    
    def __next__(self):
        """Mandelbrot set generation logic."""
        if self.iteration <= self.max_iterations:
            self.iteration += 1
            self.data['point'][self.mask] = self.data['point'][self.mask]**2 + self.template['point'][self.mask]

            divergence_mask = np.logical_and(np.absolute(self.data['point']) > 2, self.mask)
            self.data['divergence'][divergence_mask] = self.iteration
            self.mask = np.logical_and(self.mask, np.logical_not(divergence_mask))

            return (self.data, self.iteration)
        else:
            raise StopIteration