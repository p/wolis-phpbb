import threading
#import time as _time
#import random
from wolis.test_case import WolisTestCase

def make_topic(i, statuses, session, test_case, newtopic_url):
    print('Making topic %d' % (i+1))
    
    session.get(newtopic_url)
    test_case.assert_successish(session)
    
    assert 'Post a new topic' in session.response.body
    form = session.response.form(id='postform')
    elements = form.elements.mutable
    elements.set_value('subject', 'Topic one of many')
    elements.set_value('message', 'Fancy post')
    # no-js behavior is to submit the first button (save draft).
    # with js the submit button is selected as default.
    elements.submit('post')
    # code requires 2 second delta since last click, but it is
    # all client-controlled
    elements.set_value('lastclick', '0')
    test_case.check_form_key_delay()
    session.post(form.computed_action, body=elements.params.list)
    test_case.assert_successish(session)
    
    assert 'This message has been posted successfully.' in session.response.body
    statuses[i] = True

class PostLotsTest(WolisTestCase):
    # We actually do not need many posts in one topic as we can use
    # multiple topics for both searching for posts and searching for topics,
    # and post creation cannot be parallelized
    def skip_test_create_many_posts(self):
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
        
        for i in range(30):
            print('Making post %d' % (i+1))
            
            self.get(reply_url)
            self.assert_successish(self)
            
            assert 'Post a reply' in self.response.body
            form = self.response.form(id='postform')
            elements = form.elements.mutable
            elements.set_value('subject', 'Reply in topic for searching (%d)' % i)
            elements.set_value('message', 'Hello world! %d' % i)
            # no-js behavior is to submit the first button (save draft).
            # with js the submit button is selected as default.
            elements.submit('post')
            # code requires 2 second delta since last click, but it is
            # all client-controlled
            elements.set_value('lastclick', '0')
            self.check_form_key_delay()
            self.post(form.computed_action, body=elements.params.list)
            self.assert_successish(self)
            
            #while 'At least one new post has been made to this topic.' in self.response.body:
                #_time.sleep(0.5 + random.random() * 0.5)
                #form = self.response.form(id='postform')
                #elements = form.elements.mutable
                #elements.submit('post')
                #elements.set_value('lastclick', '0')
                #self.check_form_key_delay()
                #self.post(form.computed_action, body=elements.params.list)
                #self.assert_successish(self)
            
            assert 'This message has been posted successfully.' in self.response.body
    
    def test_create_many_topics(self):
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
        newtopic_url = self.response.urljoin(href)
        
        threads = []
        statuses = []
        for i in range(30):
            session = self._session.copy()
            thread = threading.Thread(target=make_topic, args=(i, statuses, session, self, newtopic_url))
            thread.start()
            threads.append(thread)
            statuses.append(False)
        
        for i in range(len(threads)):
            thread = threads[i]
            thread.join()
            assert statuses[i], 'Thread %d did not succeed' % i

if __name__ == '__main__':
    import unittest
    unittest.main()
