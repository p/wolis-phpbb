import owebunit
import urlparse
from wolis import utils
from wolis.test_case import WolisTestCase

class InstallSubsilverTestCase(WolisTestCase):
    @utils.restrict_phpbb_version('>=3.1.0')
    def test_install_subsilver(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        url = '/adm/index.php'
        self.get_with_sid(url)
        self.assert_successish()
        
        assert 'Customise' in self.response.body
        
        href = self.link_href_by_acp_tab_title('Customise')
        
        styles_url = url = urlparse.urljoin(url, href)
        self.get(url)
        self.assert_successish()
        
        assert 'Here you can manage the available styles' in self.response.body
        assert 'subsilver2' not in self.response.body
        
        href = self.link_href_by_text('Install Styles')
        
        url = urlparse.urljoin(url, href)
        self.get(url)
        self.assert_successish()
        
        assert 'Here you can install new styles.' in self.response.body
        
        href = self.link_href_by_text('Install style')
        
        url = urlparse.urljoin(url, href)
        self.get(url)
        self.assert_successish()
        
        assert 'Style "subsilver2" has been installed.' in self.response.body
        
        self.get(styles_url)
        self.assert_successish()
        
        assert 'Here you can manage the available styles' in self.response.body
        assert 'subsilver2' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
