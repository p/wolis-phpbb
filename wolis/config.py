import os.path
import yaml

class SubConfig(object):
    pass

class Config(object):
    def __init__(self, config_file_path=None):
        self.node_cmd_prefix = None
        self.php_cmd_prefix = None
        self.use_composer = False
        
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
    
    @property
    def src_path(self):
        '''If src is a path, this is src.
        If src is a url, this is src_repo_path.
        '''
        
        if self.src[0] == '/':
            return self.src
        else:
            return self.src_repo_path
    
    @property
    def gen_path(self):
        return os.path.join(self.test_root, 'gen')
    
    @property
    def sphinx_root(self):
        return os.path.join(self.test_root, 'sphinx')
    
    @property
    def sphinx_data_path(self):
        return os.path.join(self.sphinx_root, 'data')
    
    @property
    def sphinx_config_path(self):
        return os.path.join(self.sphinx_root, 'sphinx.conf')
    
    @property
    def sphinx_id_path(self):
        return os.path.join(self.sphinx_root, 'id')
    
    @property
    def sphinx_log_path(self):
        return os.path.join(self.sphinx_data_path, 'log')
