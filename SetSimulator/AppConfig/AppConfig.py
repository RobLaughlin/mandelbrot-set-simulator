from os.path import exists
import json
from PIL import Image

class AppConfig(object):
    """
    Helper class to help with app configuration.
    """

    class InvalidConfigFile(Exception):
        pass

    def __init__(self, path='config.json', autoload=True):
        self.path = None
        self.config = None
        self.set_path(path)

        if autoload:
            self.load()
            
    def get_config(self):
        return self.config
    
    def get_path(self):
        return self.path
    
    def set_path(self, path):
        if not exists(path):
            raise FileNotFoundError('File not found at given path %s.'%path)

        self.path = path

    def load(self):
        conf_file = open(self.path, 'r')
        config = None

        try:
            config = json.load(conf_file)
        except:
            raise AppConfig.InvalidConfigFile('%s is syntactically invalid. Check the syntax of the JSON before loading the config file.'%self.path)

        self.config = config
        return self.config
    
    def validate(self):
        try:
            self.config['defaults']
            self.config['defaults']['set']
            self.config['defaults']['set']['maxIterations']
            self.config['defaults']['set']['xRange']
            self.config['defaults']['set']['xRange']['min']
            self.config['defaults']['set']['xRange']['max']

            self.config['defaults']['set']['yRange']
            self.config['defaults']['set']['yRange']['min']
            self.config['defaults']['set']['yRange']['max']

            self.config['defaults']['viewer']
            self.config['defaults']['viewer']['max_animation_frame_delay']
            self.config['defaults']['viewer']['title']
            self.config['defaults']['viewer']['colormap']
            self.config['defaults']['viewer']['dimensions']
            self.config['defaults']['viewer']['dimensions']['width']
            self.config['defaults']['viewer']['dimensions']['height']
        except KeyError:
            raise KeyError('Invalid configuration file. Make sure all necessary keys and values are included in the config file.')

        return True