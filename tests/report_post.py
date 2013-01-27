from wolis.test_case import WolisTestCase

class ReportPostTestCase(WolisTestCase):
    def test_report_post(self):
        self.login('morpheus', 'morpheus')
        
        url = '/index.php'
        self.get(url)
        self.assert_successish()
        
        assert 'Index page' in self.response.body
        
        href = self.link_href_by_text('Your first forum')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        # topic
        href = self.link_href_by_text('Welcome to phpBB3')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        href = self.link_href_by_title('Report this post')
        url = self.response.urljoin(href)
        self.get(url)
        self.assert_successish()
        
        # when running repeatedly
        assert 'This post has already been reported.' not in self.response.body
        
        form = self.response.form(id='report')
        
        # submit with default fields
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'This post has been successfully reported.' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
