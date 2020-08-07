from .CoordinateRange import CoordinateRange
import numpy as np

class Mandelbrot(object):
    """
    Generates a best estimate of the Mandelbrot Set given a limit placed on recursion iterations
    """

    class TemplateNotGenerated(Exception):
        pass

    def __init__(self, iterations:int, coord_range:CoordinateRange):
        self.set = None
        self.set_template = None
        self.iterations = iterations
        self.coord_range = coord_range 

    def generate_template(self, xVals:int, yVals:int):
        """
        Takes in a number of x values and corresponding y values
        to generate a grid of complex numbers ready to be calculated.
        This is commonly used with a type of data viewer to create
        pixel points of the mandelbrot set.

        ex: generate_template(1920, 1080) 
        outputs a 2D list of complex points and their divergence point
        during the iterative process of the Mandelbrot set calculation.
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

    def get_template(self):
        return self.set_template
    
    def get_set(self):
        return self.set
    
    def get_coord_range(self):
        return self.coord_range
    
    def set_coord_range(self, coord_range:CoordinateRange):
        xRange = coord_range.get_xRange()
        yRange = coord_range.get_yRange()

        coord_range.set_xRange(xRange[0], xRange[1])
        coord_range.set_yRange(yRange[0], yRange[1])

        self.coord_range = coord_range

    def get_iterations(self):
        return self.iterations
    
    def set_iterations(self, iterations:int):
        self.iterations = iterations
    
    def generate_set(self, xVals:int=None, yVals:int=None):
        """
        Start the iterative process of generating the Mandelbrot Set.
        """

        if (xVals is None or yVals is None) and self.set_template is None:
            raise Mandelbrot.TemplateNotGenerated("Arguments 'xVals' and 'yVals' must be provided if a set template has not yet been generated")
        
        if (xVals is not None and yVals is not None):
            self.generate_template(xVals, yVals)
        elif (xVals is not None and yVals is None) or (xVals is None and yVals is not None):
            raise ValueError("Cannot have only one argument for 'xVals' and 'yVals'")

        Z = np.zeros_like(self.set_template)
        Z_Mask = np.ones_like(self.set_template, dtype=bool)
        
        for i in range(self.iterations):
            # The standard equation for the Mandelbrot Set
            Z['point'][Z_Mask] = Z['point'][Z_Mask]**2 + self.set_template['point'][Z_Mask]

            divergence_mask = np.logical_and(np.absolute(Z['point']) > 2, Z_Mask)
            Z['divergence'][divergence_mask] = i
            Z_Mask = np.logical_and(Z_Mask, np.logical_not(divergence_mask))
        
        self.set = Z