import owebunit
import os

class WolisTestCase(owebunit.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(WolisTestCase, self).__init__(*args, **kwargs)
        self.config.host = 'http://func'
        self.config.save_responses = True
        self.config.save_dir = '/var/www/func/responses'
        self.flavor = os.environ['FLAVOR']
    
    def login(self, username, password):
        params = {
            'username': username,
            'password': password,
            'login': 'Login',
        }
        
        self.post('/ucp.php?mode=login', body=params)
        self.assert_status(200)
        
        assert 'You have been successfully logged in.' in self.response.body
    
    def find_sid(self):
        cookie_names = self._session._cookie_jar.keys()
        sid_name = None
        for name in cookie_names:
            if name.endswith('_sid'):
                if sid_name is None:
                    sid_name = name
                else:
                    raise ValueError, 'Duplicate sid cookies detected: %s and %s' % (sid_name, name)
        return self._session._cookie_jar[sid_name].value
