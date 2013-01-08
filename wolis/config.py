import os.path
import yaml

class Config(object):
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/default.yml')
        with open(config_path, 'rb') as f:
            data = yaml.load(f)
        for key in data:
            setattr(self, key, data[key])
