from wolis.test_case import WolisTestCase

class AdminLogTest(WolisTestCase):
    def test_admin_log(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        url = self.response.urljoin(self.link_href_by_acp_tab_title('Maintenance'))
        self.get(url)
        self.assert_successish()
        
        # matches nav and heading
        assert 'Admin log' in self.response.body
        # matches explanation
        assert 'This lists all the actions carried out by board administrators.' in self.response.body
        # matches a log entry
        assert 'Successful administration login' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
