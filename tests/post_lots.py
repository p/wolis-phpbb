from wolis.test_case import WolisTestCase

class PostLotsTest(WolisTestCase):
    def test_create_many_posts(self):
        self.login('morpheus', 'morpheus')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('Your first forum')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        href = self.link_href_by_href_match(r'mode=post')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        assert 'Post a new topic' in self.response.body
        form = self.response.form(id='postform')
        elements = form.elements.mutable
        elements.set_value('subject', 'Topic for searching')
        elements.set_value('message', 'Frist post')
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
        
        href = self.link_href_by_text('View your submitted message')
        # topic
        self.get(self.response.urljoin(href))
        self.assert_successish()
        
        href = self.link_href_by_href_match(r'mode=reply')
        reply_url = self.response.urljoin(href)
        
        # this posts at a rate of 1 post/second,
        # meaning this test takes order of half a minute to run
        for i in range(30):
            print('Making post %d' % (i+1))
            
            self.get(reply_url)
            self.assert_successish()
            
            assert 'Post a reply' in self.response.body
            form = self.response.form(id='postform')
            elements = form.elements.mutable
            elements.set_value('subject', 'Reply in topic for searching')
            elements.set_value('message', 'Hello world! %d' % i)
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
