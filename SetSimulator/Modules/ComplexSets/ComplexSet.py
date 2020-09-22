from .CoordinateRange import CoordinateRange
import numpy as np
from abc import ABC, abstractclassmethod

class ComplexSet(ABC):
    class TemplateNotGenerated(Exception):
        pass

    def __init__(self, iterations:int, coord_range:CoordinateRange, name='Generic'):
        self.set = None
        self.set_template = None
        self.xVals = None
        self.yVals = None
        
        self.coord_range = coord_range
        self.max_iterations = iterations
        self.name = name
        self.current_iteration = 0

    def generate_template(self, xVals:int, yVals:int):
        """
        Takes in a number of x values and corresponding y values
        to generate a grid of complex numbers ready to be calculated.
        This is commonly used with a type of data viewer to create
        pixel points of the set.

        ex: generate_template(1920, 1080) 
        outputs a 2D list of complex points and their divergence point
        during the iterative process of the set calculation.
        """

        xRange = self.coord_range.get_xRange()
        yRange = self.coord_range.get_yRange()
        
        real_parts = np.linspace(xRange[0], xRange[1], xVals)
        imag_parts = np.linspace(yRange[0], yRange[1], yVals)
        real, imag = np.meshgrid(real_parts, imag_parts, indexing="xy")

        # This type is used as a wrapper to specifiy when that specific point diverges
        pointdt = np.dtype([('point', np.complex128), ('divergence', np.uint32)])

        complex_grid = np.zeros((yVals, xVals), dtype=pointdt)
        complex_grid['point'].real = real
        complex_grid['point'].imag = imag

        # Use this complex grid template before generating the Mandelbrot Set.
        self.set_template = complex_grid
        self.xVals = xVals
        self.yVals = yVals

    def get_template(self):
        return self.set_template
    
    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
    
    def get_set(self):
        return self.set
    
    def update_set(self, set_):
        self.set = set_
    
    def get_current_iteration(self):
        return self.current_iteration
    
    def get_coord_range(self):
        return self.coord_range
    
    def set_coord_range(self, coord_range:CoordinateRange):
        xRange = coord_range.get_xRange()
        yRange = coord_range.get_yRange()

        coord_range.set_xRange(xRange[0], xRange[1])
        coord_range.set_yRange(yRange[0], yRange[1])

        self.coord_range = coord_range
    
    def get_iterations(self):
        return self.max_iterations
    
    def set_iterations(self, iterations:int):
        self.max_iterations = iterations
    
    def clear_set(self):
        self.set = None
        self.current_iteration = 0

    @abstractclassmethod
    def __iter__(self):
        pass

    @abstractclassmethod
    def __next__(self):
        pass

    @abstractclassmethod
    def generate_set(self):
        pass