import os.path
import yaml

class SubConfig(object):
    pass

class Config(object):
    def __init__(self, config_file_path=None):
        self.node_cmd_prefix = None
        self.php_cmd_prefix = None
        
        if config_file_path is None:
            config_file_path = os.path.join(os.path.dirname(__file__), '../config/default.yaml')
        with open(config_file_path, 'rb') as f:
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
    
    @property
    def baseline_repo_path(self):
        return os.path.join(self.test_root, 'repo')
    
    @property
    def state_file_path(self):
        return os.path.join(self.test_root, 'state')
    
    @property
    def src_repo_path(self):
        return os.path.join(self.test_root, 'src')
