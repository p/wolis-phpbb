from wolis.test_case import WolisTestCase

class EmptyLogsTest(WolisTestCase):
    def test_empty_log(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        url = self.response.urljoin(self.link_href_by_acp_tab_title('Maintenance'))
        self.get(url)
        self.assert_successish()
        
        assert 'Admin log' in self.response.body
        
        # moderator log
        url = self.response.urljoin(self.link_href_by_text('Moderator log'))
        assert 'mode=mod' in url
        self.get(url)
        # phpbb uses the error ui here
        self.assert_successish(check_errorbox=False)
        
        assert 'No log entries for this period.' in self.response.body
        
        # user logs
        url = self.response.urljoin(self.link_href_by_text('User logs'))
        assert 'mode=users' in url
        self.get(url)
        # phpbb uses the error ui here
        self.assert_successish(check_errorbox=False)
        
        assert 'No log entries for this period.' in self.response.body
        
        # error log
        url = self.response.urljoin(self.link_href_by_text('Error log'))
        assert 'mode=critical' in url
        self.get(url)
        # phpbb uses the error ui here
        self.assert_successish(check_errorbox=False)
        
        assert 'This lists the actions carried out by the board itself.' in self.response.body
        
        if 'No log entries for this period.' not in self.response.body:
            # error log may contain an error from email being sent during
            # installation, clear it
            form = self.response.form()
            elements = form.elements.mutable
            elements.submit('delall')
            self.post(form.computed_action, elements.params.list)
            self.assert_successish(check_errorbox=False)
            
            assert 'No log entries for this period.' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
