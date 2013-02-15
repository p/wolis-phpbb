from wolis.test_case import WolisTestCase
from wolis import utils

class SearchTest(WolisTestCase):
    def test_search(self):
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        form = self.response.form(id='search')
        elements = form.elements.mutable
        elements.set_value('keywords', 'welcome')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Search found 1 match' in self.response.body
        # remove highlighting
        response_text = utils.naive_strip_html(self.response.body)
        assert 'Welcome to phpBB' in response_text

if __name__ == '__main__':
    import unittest
    unittest.main()
