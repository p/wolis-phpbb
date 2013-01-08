import owebunit
from wolis.test_case import WolisTestCase

class LoginTestCase(WolisTestCase):
    def test_login(self):
        self.get('/')
        self.assert_successish()
        
        assert 'Log out' not in self.response.body
        
        params = {
            'username': 'morpheus',
            'password': 'morpheus',
            'login': 'Login',
        }
        
        self.post('/ucp.php?mode=login', body=params)
        self.assert_successish()
        
        assert 'You have been successfully logged in.' in self.response.body
        
        self.check()
    
    def test_login_via_helper(self):
        self.login('morpheus', 'morpheus')
        
        self.check()
    
    def check(self):
        self.get('/')
        #self.get('/viewforum.php?f=1')
        self.assert_successish()
        
        assert 'Logout' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
