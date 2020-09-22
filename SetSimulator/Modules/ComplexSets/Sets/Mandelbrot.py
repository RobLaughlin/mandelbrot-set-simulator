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
    
    def __iter__(self):
        if (self.xVals is None or self.yVals is None) and self.set_template is None:
            raise Mandelbrot.TemplateNotGenerated("Arguments 'xVals' and 'yVals' must be provided if a set template has not yet been generated")
        
        if (self.xVals is not None and self.yVals is not None):
            self.generate_template(self.xVals, self.yVals)
        elif (self.xVals is not None and self.yVals is None) or (self.xVals is None and self.yVals is not None):
            raise ValueError("Cannot have only one argument for 'xVals' and 'yVals'")
        
        self._Z = np.zeros_like(self.set_template)
        self._Z_Mask = np.ones_like(self.set_template, dtype=bool)

        return self

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