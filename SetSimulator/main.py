from Modules.ComplexSets.Sets import Mandelbrot
from Modules.ComplexSets import CoordinateRange
from Modules.SetViewer import SetViewer
from AppConfig import AppConfig as Config

def init():
    conf = Config('config.json')

    if conf.validate():
        config = conf.get_config()

        # Viewer config
        viewer = config['defaults']['viewer']
        colormap = viewer['colormap']
        title = viewer['title']
        width = viewer['dimensions']['width']
        height = viewer['dimensions']['height']

        # Set config
        set_template = config['defaults']['set']
        max_iterations = set_template['maxIterations']
        xmin = set_template['xRange']['min']
        xmax = set_template['xRange']['max']
        ymin = set_template['yRange']['min']
        ymax = set_template['yRange']['max']
        crange = CoordinateRange(xmin, xmax, ymin, ymax)

        mset = Mandelbrot(iterations=max_iterations, coord_range=crange)
        sets = [mset]
        viewer = SetViewer(setlist=sets, title=title, colormap=colormap, iterations=max_iterations, dimensions=(width, height))
        viewer.show()

if __name__ == '__main__':
    init()