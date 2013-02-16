# -*- coding: utf-8 -*-

from wolis.test_case import WolisTestCase
from wolis import utils

class SearchVerifyNoBackendsTest(WolisTestCase):
    def test_backends(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        url = self.response.urljoin(self.link_href_by_acp_tab_title('Maintenance'))
        self.get(url)
        self.assert_successish()
        
        assert 'This lists all the actions carried out by board administrators.' in self.response.body
        
        url = self.response.urljoin(self.link_href_by_text('Search index'))
        assert 'mode=index' in url
        self.get(url)
        # phpbb uses the error ui here
        self.assert_successish(check_errorbox=False)
        
        assert 'Here you can manage the search backend’s indexes.' in self.response.body
        
        assert 'Delete index' not in self.response.body
        assert 'Create index' in self.response.body
    
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
