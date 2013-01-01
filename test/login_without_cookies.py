import owebunit

@owebunit.no_session
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
        
        assert 'Return to the index page' in self.response.body
        doc = self.response.lxml_etree
        continue_link = self.xpath_first(doc, '//div[@id="message"]//p/a').attrib['href']
        #print continue_link
        
        self.get(continue_link)
        self.assert_status(200)
        
        assert 'Logout' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
