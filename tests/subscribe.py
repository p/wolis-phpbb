from wolis.test_case import WolisTestCase

class SubscribeTopicTestCase(WolisTestCase):
    def test_subscribe_topic(self):
        self.login('test43', 'test42')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('Your first forum')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        # topic
        href = self.link_href_by_text('Welcome to phpBB3')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        #assert 'Unsubscribe topic' not in self.response.body
        
        href = self.link_href_by_title('Subscribe topic')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        assert 'You have subscribed to be notified of new posts in this topic.' in self.response.body
    
    def test_subscribe_forum(self):
        self.login('test43', 'test42')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('Your first forum')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        #assert 'Unsubscribe forum' not in self.response.body
        
        href = self.link_href_by_title('Subscribe forum')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        assert 'You have subscribed to be notified of new posts in this forum.' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
