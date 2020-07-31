class InvalidCoordinateBounds(Exception):
    pass

class CoordinateRange(object):
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
        if min_x >= max_x:
            raise InvalidCoordinateBounds('The maximum x value must be strictly greater than the minimum x value.')

        self.xRange = (min_x, max_x)
    
    def get_yRange(self):
        return self.yRange
    
    def set_yRange(self, min_y:float, max_y:float):
        if min_y >= max_y:
            raise InvalidCoordinateBounds('The maximum y value must be strictly greater than the minimum y value.')

        self.yRange = (min_y, max_y)
    
    def __str__(self):
        return 'xRange:' + str(self.xRange) + '\nyRange:' + str(self.yRange)