import itertools
from ..ComplexSet import ComplexSet
from ..CoordinateRange import CoordinateRange
import numpy as np

class Mandelbrot(ComplexSet):
    """
    Generates a best estimate of the Mandelbrot Set given a limit placed on recursion iterations
    """
    def __init__(self, iterations:int, coord_range:CoordinateRange):
        super().__init__(iterations, coord_range, 'Mandelbrot')

    def __next__(self):
        if self.current_iteration <= self.max_iterations:
            self.current_iteration += 1
            
            self._Z['point'][self._Z_Mask] = self._Z['point'][self._Z_Mask]**2 + self.set_template['point'][self._Z_Mask]

            divergence_mask = np.logical_and(np.absolute(self._Z['point']) > 2, self._Z_Mask)
            self._Z['divergence'][divergence_mask] = self.current_iteration
            self._Z_Mask = np.logical_and(self._Z_Mask, np.logical_not(divergence_mask))
            self.set = self._Z
            
            return (self.set, self.current_iteration)
        else:
            raise StopIteration
    
    def generate_set(self):
        self.clear_set()
        for _ in range(0, self.max_iterations):
            next(self)