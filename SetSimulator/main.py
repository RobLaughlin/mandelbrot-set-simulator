import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np
import sys
import time
import math
import colorsys as colors

# Small helper class for data formatting
class CoordinateSpace:
    def __init__(self, x_min, x_max, y_min, y_max):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

# Wrapper function for color conversion, resulting with cleaner code in the recursion loop
def hsv_to_rgb(hues):
    color_space = []

    for hue in hues:
        color_space.append(tuple(round(i * 255) for i in colors.hsv_to_rgb(hue,1,1)))

    return color_space

"""
Generates a best estimate of the Mandelbrot Set given a limit
on recursion iterations and a point of divergence (Most commonly a radius of 2)
"""
class Mandelbrot:
    def __init__(self, recursionLimit=255, divergentPoint=2):
        self.recursionLimit = recursionLimit
        self.divergentPoint = divergentPoint

    """
    Performs the same operation as converting complex co-ordinates into
    colors as the color_map override in the Mandelbrot subclasses, however
    is abstracted to where the animation process is removed completely.
    This function ONLY handles the process of (r, i) => (R, G, B) based on iterations.
    """
    def color_map(self, complex_grid:np.ndarray):
        Z = np.zeros_like(complex_grid)
        Z_Mask = np.ones_like(complex_grid, dtype=bool)
        pixel_map = np.zeros((complex_grid.shape[0], complex_grid.shape[1], 3), dtype=np.uint8)

        hues = np.linspace(0, 1, num=self.recursionLimit)
        RGB_space = hsv_to_rgb(hues)

        for i in range(self.recursionLimit):
            Z[Z_Mask] = Z[Z_Mask]**2 + complex_grid[Z_Mask]
            pixel_mask = np.logical_and(np.absolute(Z) > self.divergentPoint, Z_Mask)
            pixel_map[pixel_mask, :] = RGB_space[i]
            Z_Mask = np.logical_and(Z_Mask, np.logical_not(pixel_mask))
            im.set_array(pixel_map)
        
        return pixel_map

    """
    Starts the image generation process by converting
    width and height into a 2D array of complex co-ordinates
    """
    def generate_image(self, width, height, coords:CoordinateSpace):
        x_scale = width / height

        complex_grid = np.zeros((height, width), dtype=np.complex)
        real_parts = np.linspace(coords.x_min * x_scale, coords.x_max * x_scale, num=width)
        imag_parts = np.linspace(coords.y_min, coords.y_max, num=height)
        real, imag = np.meshgrid(real_parts, imag_parts, indexing="xy")
        complex_grid.real = real
        complex_grid.imag = imag

        return self.color_map(complex_grid)

"""
Extends the Mandelbrot class with additional functionality
regarding animation and picture viewing in pyplot
"""
class Mandelbrot_Viewer(Mandelbrot):
    def __init__(self, recursionLimit, divergentPoint, width, height, zoom, coords:CoordinateSpace):
        super().__init__(recursionLimit, divergentPoint)
        self.width = width
        self.height = height
        self.zoom_base = zoom
        self.coords = coords
        self.anim = None
        self.zoom_level = 0
        self.DPI = 100
        self.animation_delay = 10

        self.fig = plt.figure()
        self.axes = plt.gca()
        self.fig.set_size_inches(width / self.DPI, height / self.DPI)

        # Left/Right click zoom handler
        self.fig.canvas.mpl_connect('button_press_event', self.click_handler)

    def show_image(self):
        self.generate_image(self.width, self.height, self.coords)

    """
    Takes a 2D array of complex numbers as input and outputs an RGB
    color map based on iterations of diveregence for each complex number
    """
    def color_map(self, complex_grid:np.ndarray):
        global Z, Z_Mask, pixel_map, im, i, RGB_space
        Z = np.zeros_like(complex_grid)
        Z_Mask = np.ones_like(complex_grid, dtype=bool)
        pixel_map = np.zeros((complex_grid.shape[0], complex_grid.shape[1], 3), dtype=np.uint8)
        im = plt.imshow(pixel_map, animated=True, origin="lower")

        hues = np.linspace(0, 1, num=self.recursionLimit)
        RGB_space = hsv_to_rgb(hues)
        
        # Render loop for pyplot animation
        i = 0
        def render(*args):
            global Z, Z_Mask, pixel_map, im, i, RGB_space
            Z[Z_Mask] = Z[Z_Mask]**2 + complex_grid[Z_Mask]
            pixel_mask = np.logical_and(np.absolute(Z) > self.divergentPoint, Z_Mask)
            pixel_map[pixel_mask, :] = RGB_space[i % self.recursionLimit]
            Z_Mask = np.logical_and(Z_Mask, np.logical_not(pixel_mask))
            im.set_array(pixel_map)
            i += 1
            return [im]
        
        self.anim = anim.FuncAnimation( fig=self.fig, func=render, frames=self.recursionLimit, 
                                        interval=self.animation_delay, blit=True, repeat=False, 
                                        cache_frame_data=False)
        plt.show()

        return pixel_map

    def click_handler(self, event):
        if (event.xdata == None or event.ydata == None):
            return
        
        #Interactive mode used here to prevent a terminal stalling bug when closing the program after clicked
        plt.ion() 

        # Stop any and all animation when clicked
        self.anim.event_source.stop()
        self.anim = None
        
        # Get (r, i) => (x, y) co-ordinate pairs on complex plane
        relative_x = self.coords.x_min + (event.xdata / self.width) * (self.coords.x_max - self.coords.x_min)
        relative_y = self.coords.y_min + (event.ydata / self.height) * (self.coords.y_max - self.coords.y_min)

        if str(event.button) == "MouseButton.LEFT":
            self.zoom_level += 1
        elif str(event.button) == "MouseButton.RIGHT":
            self.zoom_level -= 1
        
        """
        Reads the correct co-ordinates in the complex plane,
        then creates an appropriate box around the co-ordinates based on zoom level.
        Here the complex plane co-ordinates are (relative_x, relative_y) => (r, i), and
        zoom_base**zoom_level are the viewer bounds.
        """
        relative_bound = (self.zoom_base**self.zoom_level)
        self.coords.x_min = relative_x - relative_bound
        self.coords.x_max = relative_x + relative_bound
        self.coords.y_min = relative_y - relative_bound
        self.coords.y_max = relative_y + relative_bound    
        self.show_image()
        plt.draw()

def save_image(fileName):
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(fileName, bbox_inches = 'tight', pad_inches = 0)

def init():
    coordinate_space = CoordinateSpace(x_min=-2, x_max=2, y_min=-2, y_max=2)
    viewer = Mandelbrot_Viewer(recursionLimit=1000, divergentPoint=2, width=600, height=600, zoom=0.25, coords=coordinate_space)
    viewer.axes.set_axis_off()
    viewer.show_image()

if __name__ == "__main__":
    init()