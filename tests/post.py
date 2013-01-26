import urlparse
from wolis.test_case import WolisTestCase

class PostTestCase(WolisTestCase):
    def test_create_topic(self):
        self.login('morpheus', 'morpheus')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('Your first forum')
        url = urlparse.urljoin(url, href)
        self.get(url)
        self.assert_successish()
        
        href = self.link_href_by_href_match(r'mode=post')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        assert 'Post a new topic' in self.response.body
        form = self.response.form(id='postform')
        elements = form.elements.mutable
        elements.set_value('subject', 'Cookies are awesome')
        elements.set_value('message', 'Cookies are great and very nice')
        # no-js behavior is to submit the first button (save draft).
        # with js the submit button is selected as default.
        elements.submit('post')
        # code requires 2 second delta since last click, but it is
        # all client-controlled
        elements.set_value('lastclick', '0')
        self.check_form_key_delay()
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'This message has been posted successfully.' in self.response.body
    
    def test_post_reply(self):
        self.login('morpheus', 'morpheus')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('Your first forum')
        url = urlparse.urljoin(url, href)
        self.get(url)
        self.assert_successish()
        
        # topic
        href = self.link_href_by_text('Welcome to phpBB3')
        url = urlparse.urljoin(url, href)
        self.get(url)
        self.assert_successish()
        
        href = self.link_href_by_href_match(r'mode=reply')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        assert 'Post a reply' in self.response.body
        form = self.response.form(id='postform')
        elements = form.elements.mutable
        elements.set_value('subject', 'Replies are awesome')
        elements.set_value('message', 'Reptiles are also not bad')
        # no-js behavior is to submit the first button (save draft).
        # with js the submit button is selected as default.
        elements.submit('post')
        # code requires 2 second delta since last click, but it is
        # all client-controlled
        elements.set_value('lastclick', '0')
        self.check_form_key_delay()
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'This message has been posted successfully.' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
