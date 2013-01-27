from wolis.test_case import WolisTestCase
from wolis import utils
import lxml.etree
import webracer.utils

xpath_first_check = webracer.utils.xpath_first_check

class SearchPaginationTest(WolisTestCase):
    def test_one_result_page(self):
        url = '/search.php?keywords=frist'
        self.get(url)
        self.assert_successish()
        
        assert 'Search found 1 match' in self.response.body
        # remove highlighting
        response_text = utils.naive_strip_html(self.response.body)
        assert 'Frist post' in response_text
        
        # it is in a title attribute
        assert 'Click to jump to page' not in self.response.body
    
    def test_many_result_pages(self):
        url = '/search.php?keywords=searching'
        self.get(url)
        self.assert_successish()
        
        assert 'Search found' in self.response.body
        # remove highlighting
        response_text = utils.naive_strip_html(self.response.body)
        assert 'Reply in topic' in response_text
        
        assert 'Click to jump to page' in self.response.body
        
        # check active page
        active = xpath_first_check(self.response.lxml_etree, '//li[@class="active"]')
        text = lxml.etree.tostring(active, method='text').strip()
        assert text == '1'
    
    def test_legitimate_offset(self):
        url = '/search.php?keywords=searching&start=10'
        self.get(url)
        self.assert_successish()
        
        assert 'Search found' in self.response.body
        # remove highlighting
        response_text = utils.naive_strip_html(self.response.body)
        assert 'Reply in topic' in response_text
        
        assert 'Click to jump to page' in self.response.body
        
        # check active page
        active = xpath_first_check(self.response.lxml_etree, '//li[@class="active"]')
        text = lxml.etree.tostring(active, method='text').strip()
        assert text == '2'
    
    def test_negative_offset(self):
        url = '/search.php?keywords=searching&start=-10'
        self.get(url)
        self.assert_successish()
        
        assert 'Search found' in self.response.body
        # remove highlighting
        response_text = utils.naive_strip_html(self.response.body)
        assert 'Reply in topic' in response_text
        
        assert 'Click to jump to page' in self.response.body
        
        # check active page
        active = xpath_first_check(self.response.lxml_etree, '//li[@class="active"]')
        text = lxml.etree.tostring(active, method='text').strip()
        assert text == '1'

if __name__ == '__main__':
    import unittest
    unittest.main()
