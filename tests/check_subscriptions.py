from wolis.test_case import WolisTestCase

class CheckSubscriptionsTestCase(WolisTestCase):
    def test_check_subscriptions(self):
        self.login('test43', 'test42')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('User Control Panel')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        # subscriptions
        href = self.link_href_by_text('Manage subscriptions')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        assert 'You are not subscribed to any forums' not in self.response.body
        assert 'You are not subscribed to any topics' not in self.response.body
        
        assert 'Welcome to phpBB3' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
