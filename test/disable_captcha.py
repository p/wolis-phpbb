import owebunit
import urlparse
from wolis_test_case import WolisTestCase

class AcpLoginTestCase(WolisTestCase):
    def test_disable_captcha(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_status(200)
        
        assert 'Board statistics' in self.response.body
        
        url = self.link_href_by_text('Spambot countermeasures')
        
        # already has sid
        self.get(urlparse.urljoin(start_url, url))
        self.assert_status(200)
        
        assert 'Enable spambot countermeasures' in self.response.body
        
        assert len(self.response.forms) == 1
        form = self.response.forms[0]
        
        params = {
            'enable_confirm': '0',
        }
        params = owebunit.extend_params(form.params.list, params)
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        assert 'Configuration updated successfully' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
