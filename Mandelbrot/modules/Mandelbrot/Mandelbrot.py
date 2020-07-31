from CoordinateRange.CoordinateRange import CoordinateRange as cRange

class Mandelbrot():
    """
    Generates a best estimate of the Mandelbrot Set given a limit placed on recursion iterations
    """

    def __init__(self, iterations:int, coord_range:cRange):
        self.iterations = None
        self.set_iterations(iterations)

        self.coord_range = None
        self.set_coord_range(coord_range)

    def get_coord_range(self):
        return self.coord_range
    
    def set_coord_range(self, coord_range:cRange):
        if coord_range is None:
            raise TypeError("Argument 'coord_range' is required.")
        
        xRange = coord_range.get_xRange()
        yRange = coord_range.get_yRange()

        coord_range.set_xRange(xRange[0], xRange[1])
        coord_range.set_yRange(yRange[0], yRange[1])

        self.coord_range = coord_range

    def get_iterations(self):
        return self.iterations
    
    def set_iterations(self, iterations:int):
        if iterations is None or not isinstance(iterations, int):
            raise TypeError("Expected an int for argument 'iterations'")
        
        self.iterations = iterations
