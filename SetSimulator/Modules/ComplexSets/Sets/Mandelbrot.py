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
        """
        Start the iterative process of generating the Mandelbrot Set.
        """

        if (self.xVals is None or self.yVals is None) and self.set_template is None:
            raise Mandelbrot.TemplateNotGenerated("Arguments 'xVals' and 'yVals' must be provided if a set template has not yet been generated")
        
        if (self.xVals is not None and self.yVals is not None):
            self.generate_template(self.xVals, self.yVals)
        elif (self.xVals is not None and self.yVals is None) or (self.xVals is None and self.yVals is not None):
            raise ValueError("Cannot have only one argument for 'xVals' and 'yVals'")

        Z = np.zeros_like(self.set_template)
        Z_Mask = np.ones_like(self.set_template, dtype=bool)
        
        for i in range(self.max_iterations):
            # The standard equation for the Mandelbrot Set
            Z['point'][Z_Mask] = Z['point'][Z_Mask]**2 + self.set_template['point'][Z_Mask]

            divergence_mask = np.logical_and(np.absolute(Z['point']) > 2, Z_Mask)
            Z['divergence'][divergence_mask] = i
            Z_Mask = np.logical_and(Z_Mask, np.logical_not(divergence_mask))
            yield (Z, i)
    
    def __next__(self):
        if self.current_iteration <= self.max_iterations:
            next_set = next(self.__iter__())
            self.set = next_set[0]
            self.current_iteration = next_set[1]
            return next_set
        else:
            raise StopIteration
    
    def generate_set(self):
        for i in range(0, self.max_iterations):
            self.__next__()