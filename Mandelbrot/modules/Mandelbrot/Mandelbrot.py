from CoordinateRange.CoordinateRange import CoordinateRange as cRange
import numpy as np

class Point2d(object):
    """ A simple wrapper to represent cartesian points."""
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x
    
    def set_x(self, x:float):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self, y:float):
        self.y = y

class MandelbrotPoint(Point2d):
    def __init__(point:complex, divergence_point:int):
        super().__init__(point.real, point.imag)
        self.divergence_point = divergence_point
    
    def get_divergence_point(self):
        return self.divergence_point

    def set_divergence_point(self, divergence_point:int):
        self.divergence_point = divergence_point

class Mandelbrot(object):
    """
    Generates a best estimate of the Mandelbrot Set given a limit placed on recursion iterations
    """

    def __init__(self, iterations:int, coord_range:cRange):
        self.set = None
        self.iterations = iterations
        self.coord_range = coord_range

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
    
    def generate_set(self, xVals:int, yVals:int):
        """
        Start the iterative process of generating the Mandelbrot Set.
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

        Z = np.zeros_like(complex_grid)
        Z_Mask = np.ones_like(complex_grid, dtype=bool)
        
        for i in range(self.iterations):
            # The standard equation for the Mandelbrot Set
            Z['point'][Z_Mask] = Z['point'][Z_Mask]**2 + complex_grid['point'][Z_Mask]
            divergence_mask = np.logical_and(np.absolute(Z['point']) > 2, Z_Mask)
            Z['divergence'][divergence_mask] = i
            Z_Mask = np.logical_and(Z_Mask, np.logical_not(divergence_mask))
        
        self.set = Z

if __name__ == '__main__':
    coord_range = cRange(-2, 2, -2, 2)
    mSet = Mandelbrot(iterations = 255, coord_range=coord_range)
    mSet.generate_set(600, 600)
    print(mSet.set)
        

        


