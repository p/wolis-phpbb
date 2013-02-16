# -*- coding: utf-8 -*-

from wolis.test_case import WolisTestCase
from wolis import utils

class SphinxVerifySearchFailsTest(WolisTestCase):
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
        
        assert 'Sorry, search could not be performed' in self.response.body
    
    def test_search_with_admin_credentials(self):
        self.login('morpheus', 'morpheus')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        form = self.response.form(id='search')
        elements = form.elements.mutable
        # Use the same keywords that we test elsewhere return results
        elements.set_value('keywords', 'welcome')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Search failed: connection to localhost:9339 failed' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
