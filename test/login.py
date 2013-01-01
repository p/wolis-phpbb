import owebunit

class LoginTestCase(owebunit.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(LoginTestCase, self).__init__(*args, **kwargs)
        self.config.host = 'http://func'
    
    def test_login(self):
        self.get('/')
        self.assert_status(200)
        
        assert 'Log out' not in self.response.body
        
        params = {
            'username': 'morpheus',
            'password': 'morpheus',
            'login': 'Login',
        }
        
        self.post('/ucp.php?mode=login', body=params)
        self.assert_status(200)
        
        assert 'You have been successfully logged in.' in self.response.body
        
        self.get('/')
        #self.get('/viewforum.php?f=1')
        self.assert_status(200)
        
        assert 'Logout' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
