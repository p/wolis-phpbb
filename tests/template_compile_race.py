import threading
from wolis.test_case import WolisTestCase
from wolis import utils

thread_count = 5
requests_per_thread = 20

stop = False
failed = False

def test_fn(s, case, url):
    global stop, failed
    
    for i in range(requests_per_thread):
        if stop:
            break
        s.get(url)
        case.assert_successish(s)
        if 'Subject:' not in s.response.body:
            failed = True
            stop = True

class TemplateCompileRaceTest(WolisTestCase):
    def skip_test_race(self):
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
        
        threads = []
        for i in range(thread_count):
            session = self._session.copy()
            session.config.retry_failed = True
            session.config.retry_condition = utils.retry_condition_fn
            thread = threading.Thread(target=test_fn, args=(session, self, url))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
        
        global failed
        assert not failed

if __name__ == '__main__':
    import unittest
    unittest.main()
