import owebunit
import urlparse
from wolis.test_case import WolisTestCase

class SetSubsilverDefaultTestCase(WolisTestCase):
    def test_install_subsilver(self):
        self.get('/')
        self.assert_successish()
        
        assert 'style/subsilver' not in self.response.body
        
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
        assert 'subsilver2' in self.response.body
        
        doc = self.response.lxml_etree
        subsilver = self.xpath_first(doc, '//*[text()="subsilver2"]/ancestor::tr')
        details = self.xpath_first(subsilver, './/a[descendant-or-self::*/text()="Details"]')
        
        url = urlparse.urljoin(styles_url, details.attrib['href'])
        self.get(url)
        self.assert_successish()
        
        assert len(self.response.forms) == 1
        form = self.response.forms[0]
        elements = form.elements.mutable
        elements.set_value('style_default', '1')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        # get style details page again
        self.get(url)
        self.assert_successish()
        
        assert 'style_active' in self.response.body
        assert 'style_default' not in self.response.body
        
        # this is not what it does at all
        if False:
            with self.session() as s:
                s.get('/')
                self.assert_successish(s)
                
                assert 'style/subsilver' in s.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
