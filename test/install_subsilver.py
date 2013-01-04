import owebunit
import urlparse
from wolis_test_case import WolisTestCase

class AcpKnobsTestCase(WolisTestCase):
    def test_install_subsilver(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        url = '/adm/index.php'
        self.get_with_sid(url)
        self.assert_successish()
        
        assert 'Customise' in self.response.body
        
        doc = self.response.lxml_etree
        link = self.xpath_first(doc, '//div[@id="tabs"]//a[descendant-or-self::*/text()="Customise"]')
        
        styles_url = url = urlparse.urljoin(url, link.attrib['href'])
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
        
        doc = self.response.lxml_etree
        subsilver = self.xpath_first(doc, '//*[text()="subsilver2"]/ancestor::tr')
        uninstall = self.xpath_first(subsilver, './/a[descendant-or-self::*/text()="Uninstall"]')
        
        url = urlparse.urljoin(styles_url, uninstall.attrib['href'])
        self.get(url)
        self.assert_successish()
        
        assert len(self.response.forms) == 1
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'Style "subsilver2" uninstalled successfully.' in self.response.body
        
        styles_url = url = urlparse.urljoin(url, link.attrib['href'])
        self.get(url)
        self.assert_successish()
        
        assert 'Here you can manage the available styles' in self.response.body
        assert 'subsilver2' not in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
