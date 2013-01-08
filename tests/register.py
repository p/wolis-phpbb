import owebunit
from wolis.wolis_test_case import WolisTestCase

class RegisterTestCase(WolisTestCase):
    def test_register(self):
        self.get('/ucp.php?mode=register')
        self.assert_successish()
        
        assert 'Registration' in self.response.body
        
        # first form is search box
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        elements = form.elements.mutable
        elements.submit('agreed')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Username:' in self.response.body
        
        # first form is search box
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        # for repeated runs
        suffix = self.random_suffix()
        params = {
            'username': 'test' + suffix,
            'new_password': 'test42',
            'password_confirm': 'test42',
            'email': 'foo%s@bar.local' % suffix,
            'lang': 'en',
            'tz': 'UTC',
            'confirm_id': '',
            'confirm_code': '',
        }
        
        if self.flavor == 'olympus':
            params['email_confirm'] = params['email']
        
        self.check_form_key_delay()
        
        elements = form.elements.mutable
        elements.submit('submit')
        params = owebunit.extend_params(elements.params.dict, params)
        self.post(form.computed_action, body=params)
        self.assert_successish()
        
        assert 'Registration' not in self.response.body
        assert 'Thank you for registering' in self.response.body
        # check that there are no further actions needed
        assert 'You may now login with your username' in self.response.body
    
    def test_initial_timezone_ascreus(self):
        self.get('/ucp.php?mode=register&agreed=yes')
        self.assert_successish()
        
        assert 'Username:' in self.response.body
        
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        assert form.params.dict['tz_date'].startswith('GMT+11:00')
        
        #doc = self.response.lxml_etree
        #timezone_select = self.xpath_first(doc, 'select[@id="timezone"]')

if __name__ == '__main__':
    import unittest
    unittest.main()
