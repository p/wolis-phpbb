import owebunit

class RegisterTestCase(owebunit.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(RegisterTestCase, self).__init__(*args, **kwargs)
        self.config.host = 'http://func'
    
    def test_register(self):
        self.get('/ucp.php?mode=register')
        self.assert_status(200)
        
        assert 'Registration' in self.response.body
        
        # first form is search box
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        params = form.params.submit('agreed').list
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        assert 'Username:' in self.response.body
        
        # first form is search box
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        params = {
            'username': 'test',
            'new_password': 'test42',
            'password_confirm': 'test42',
            'email': 'foo@bar.local',
            'lang': 'en',
            'tz': 'UTC',
            'confirm_id': '',
            'confirm_code': '',
        }
        
        params = owebunit.extend_params(dict(form.params.submit('submit').list), params)
        #print params
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        #print self.response.body
        assert 'Registration' not in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
