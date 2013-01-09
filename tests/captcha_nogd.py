import owebunit
import owebunit.utils
import urlparse
import re
import Image
import cStringIO as StringIO
from wolis.test_case import WolisTestCase

xpath_first = owebunit.utils.xpath_first
xpath_first_check = owebunit.utils.xpath_first_check

class CaptchaNogdTestCase(WolisTestCase):
    def test_100_settings(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        href = self.link_href_by_text('Spambot countermeasures')
        url = urlparse.urljoin(start_url, href)
        self.get(url)
        self.assert_successish
        
        assert 'Enable spambot countermeasures' in self.response.body
        
        doc = self.response.lxml_etree
        nogd_option = xpath_first_check(doc, '//option[@value="phpbb_captcha_nogd"]')
        assert 'selected' in nogd_option.attrib
        assert nogd_option.attrib['selected'] == 'selected'
    
    def test_200_captcha(self):
        self.get('/ucp.php?mode=confirm&confirm_id=000&type=1')
        self.assert_successish()
        
        io = StringIO.StringIO(self.response.body)
        im = Image.open(io)
        assert im.format == 'PNG'

if __name__ == '__main__':
    import unittest
    unittest.main()
