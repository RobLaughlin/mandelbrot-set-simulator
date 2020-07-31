from CoordinateRange.CoordinateRange import CoordinateRange as cRange
import numpy as np

class MandelbrotTemplateNotGenerated(Exception):
    pass

class Mandelbrot(object):
    """
    Generates a best estimate of the Mandelbrot Set given a limit placed on recursion iterations
    """

    def __init__(self, iterations:int, coord_range:cRange):
        self.set = None
        self.__set_template = None
        self.iterations = iterations
        self.coord_range = coord_range 

    def generate_template(self, xVals:int, yVals:int):
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
        self.__set_template = complex_grid

    def get_set(self):
        return self.set
    
    def get_coord_range(self):
        return self.coord_range
    
    def set_coord_range(self, coord_range:cRange):
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

        if (xVals is None or yVals is None) and self.__set_template is None:
            raise MandelbrotTemplateNotGenerated("Arguments 'xVals' and 'yVals' must be provided if a set template has not yet been generated")
        
        if (xVals is not None and yVals is not None):
            self.generate_template(xVals, yVals)
        elif (xVals is not None and yVals is None) or (xVals is None and yVals is not None):
            raise ValueError("Cannot have only one argument for 'xVals' and 'yVals'")

        Z = np.zeros_like(self.__set_template)
        Z_Mask = np.ones_like(self.__set_template, dtype=bool)
        
        for i in range(self.iterations):
            # The standard equation for the Mandelbrot Set
            Z['point'][Z_Mask] = Z['point'][Z_Mask]**2 + self.__set_template['point'][Z_Mask]
            divergence_mask = np.logical_and(np.absolute(Z['point']) > 2, Z_Mask)
            Z['divergence'][divergence_mask] = i
            Z_Mask = np.logical_and(Z_Mask, np.logical_not(divergence_mask))
        
        self.set = Z
        