import owebunit
from wolis_test_case import WolisTestCase

@owebunit.no_session
class LoginWithoutCookiesTestCase(WolisTestCase):
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
        
        assert 'Return to the index page' in self.response.body
        doc = self.response.lxml_etree
        continue_link = self.xpath_first(doc, '//div[@id="message"]//p/a').attrib['href']
        #print continue_link
        
        self.get(continue_link)
        self.assert_successish()
        
        assert 'Logout' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
