import json
from Modules.ComplexSets.Sets import Mandelbrot, Julia
from Modules.ComplexSets import CoordinateRange
from Modules.SetViewer import SetViewer

def init():
    try:
        config = json.load(open('config.json', 'r'))

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
        
        julia_constant = set_template['julia_constant']['real'] + set_template['julia_constant']['imag'] * 1j
        crange = CoordinateRange(xmin, xmax, ymin, ymax)
        mset = Mandelbrot(iterations=max_iterations, coord_range=crange, xy_vals=(width, height))
        jset = Julia(iterations=max_iterations, coord_range=crange, constant=julia_constant, xy_vals=(width, height))
        sets = [mset, jset]

        viewer = SetViewer(setlist=sets, title=title, colormap=colormap, iterations=max_iterations, julia_constant=julia_constant, 
                            dimensions=(width, height), max_interval_delay=max_anim_frame_delay, maintain_ratio=viewer['maintain_aspect_ratio'])
        viewer.show()
    
    except:
        print('Invalid configuration file.')

if __name__ == '__main__':
    init()