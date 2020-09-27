from ..ComplexSet import ComplexSet
from ..CoordinateRange import CoordinateRange
import numpy as np

class Julia(ComplexSet):
    """Procedurally generates the Julia set given a constant.

    Args:
        iterations (int): The maximum number of iterations for Julia set generation.
        coord_range (coordinaterange) ((float, float), (float, float)): X and Y range values, respectively.
        xy_vals (tuple) (int, int): How many intervals to split the x and y axis into.
        constant (complex): The complex number to use for the Julia set generation.
    
    Attributes:
        constant (complex): The complex number to use for the Julia set generation.
    
    """
    def __init__(self, iterations:int, coord_range:CoordinateRange, xy_vals:tuple, constant:complex):
        super().__init__(iterations, coord_range,  xy_vals, 'Julia')
        self._constant = constant

    @property
    def constant(self) -> complex:
        """complex: The complex number to use for the Julia set generation."""
        return self._constant
    
    @constant.setter
    def constant(self, constant:complex):
        self._constant = constant
    
    def __iter__(self):
        """Iteration wrapper to setup the Julia set generation."""
        super().__iter__()
        self.data = self.template
        return self

    def __next__(self):
        """Julia set generation logic."""
        if self.iteration <= self.max_iterations:
            self.iteration += 1
            self.data['point'][self.mask] = self.data['point'][self.mask]**2 + self.constant

            divergence_mask = np.logical_and(np.absolute(self.data['point']) > 2, self.mask)
            self.data['divergence'][divergence_mask] = self.iteration
            self.mask = np.logical_and(self.mask, np.logical_not(divergence_mask))
            return (self.data, self.iteration)
        else:
            raise StopIteration