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
        max_anim_frame_delay = viewer['max_animation_frame_delay']

        # Set config
        set_template = config['defaults']['set']
        max_iterations = set_template['maxIterations']
        xmin = float(set_template['xRange']['min'])
        xmax = float(set_template['xRange']['max'])
        ymin = float(set_template['yRange']['min'])
        ymax = float(set_template['yRange']['max'])

        if viewer['maintain_aspect_ratio']:
            ratio = width / height
            pad = ((ratio - 1) * (xmax - xmin)) / 2
            xmin -= pad
            xmax += pad

        crange = CoordinateRange(xmin, xmax, ymin, ymax)
        mset = Mandelbrot(iterations=max_iterations, coord_range=crange)
        sets = [mset]
        viewer = SetViewer(setlist=sets, title=title, colormap=colormap, iterations=max_iterations, 
                            dimensions=(width, height), max_interval_delay=max_anim_frame_delay)
        viewer.show()

if __name__ == '__main__':
    init()