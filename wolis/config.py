import os.path
import yaml

class SubConfig(object):
    pass

class Config(object):
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/default.yml')
        with open(config_path, 'rb') as f:
            data = yaml.load(f)
        for key in data:
            value = data[key]
            if key == 'db':
                assert isinstance(value, dict)
                mapped_value = SubConfig()
                for subkey in value:
                    mapped_value.__dict__[subkey] = value[subkey]
                value = mapped_value
            setattr(self, key, value)
