# -*- coding: utf-8 -*-

from wolis.test_case import WolisTestCase
from wolis import utils

class SearchVerifyNoResultsTest(WolisTestCase):
    def test_search(self):
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        form = self.response.form(id='search')
        elements = form.elements.mutable
        # Use the same keywords that we test elsewhere return results
        elements.set_value('keywords', 'welcome')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'No posts were found' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
