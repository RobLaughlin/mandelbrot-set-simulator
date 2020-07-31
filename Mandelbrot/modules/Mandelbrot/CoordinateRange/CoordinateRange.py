class InvalidCoordinateBounds(Exception):
    pass

class CoordinateRange():
    def __init__(self, minX:float, maxX:float, minY:float, maxY:float):
        """
        Sets a strict boundary between x and y values.
        """
        self.xRange = None
        self.set_xRange(minX, maxX)

        self.yRange = None
        self.set_yRange(minY, maxY)

    def get_xRange(self):
        return self.xRange
    
    def set_xRange(self, min_x:float, max_x:float):
        if min_x is None or not isinstance(min_x, (float, int)):
            raise TypeError("Expected a float for argument 'min_x'")

        if max_x is None or not isinstance(max_x, (float, int)):
            raise TypeError("Expected a float for argument 'max_x'")
        
        if min_x >= max_x:
            raise InvalidCoordinateBounds('The maximum x value must be strictly greater than the minimum x value.')

        self.xRange = (min_x, max_x)
    
    def get_yRange(self):
        return self.yRange
    
    def set_yRange(self, min_y:float, max_y:float):
        if min_y is None or not isinstance(min_y, (float, int)):
            raise TypeError("Expected a float for argument 'min_y'")

        if max_y is None or not isinstance(max_y, (float, int)):
            raise TypeError("Expected a float for argument 'max_y'")
        
        if min_y >= max_y:
            raise InvalidCoordinateBounds('The maximum y value must be strictly greater than the minimum y value.')

        self.yRange = (min_y, max_y)
    
    def __str__(self):
        return 'xRange:' + str(self.xRange) + '\nyRange:' + str(self.yRange)