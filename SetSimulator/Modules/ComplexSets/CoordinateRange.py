class InvalidCoordinateBounds(Exception):
    """Raised if one or more minimum is greater than the respective maximum value."""
    pass

class CoordinateRange(object):
    """Sets a strict boundary between x and y values.

    Args:
        minX (float): Minimum x value.
        maxX (float): Maximum x value.
        minY (float): Minimum y value.
        maxY (float): Maximum y value.
    
    Raises:
        InvalidCoordinateBounds: If one or more minimum is greater than the respective maximum value.
    
    """
    def __init__(self, minX:float, maxX:float, minY:float, maxY:float):

        self._x_range = (minX, maxX)
        self._y_range = (minY, maxY)

    @property
    def x_range(self) -> tuple:
        """tuple (float, float): The minimum and maximum bounds of the x range, respectively."""
        return self._x_range

    @x_range.setter
    def x_range(self, x_range:tuple):
        if x_range[0] >= x_range[1]:
            raise InvalidCoordinateBounds('The maximum x value must be strictly greater than the minimum x value.')

        self._x_range = x_range
    
    @property
    def y_range(self):
        """tuple (float, float): The minimum and maximum bounds of the y range, respectively."""
        return self._y_range

    @y_range.setter
    def y_range(self, y_range:tuple):
        if y_range[0] >= y_range[1]:
            raise InvalidCoordinateBounds('The maximum y value must be strictly greater than the minimum y value.')

        self._y_range = y_range
    
    def __str__(self):
        return 'xRange:' + str(self.x_range) + '\nyRange:' + str(self.y_range)