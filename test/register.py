import owebunit
from wolis_test_case import WolisTestCase

class RegisterTestCase(WolisTestCase):
    def test_register(self):
        self.get('/ucp.php?mode=register')
        self.assert_status(200)
        
        assert 'Registration' in self.response.body
        
        # first form is search box
        assert len(self.response.forms) == 2
        form = self.response.forms[1]
        
        params = form.params.submit('agreed').list
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
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
        
        self.check_form_key_delay()
        
        params = owebunit.extend_params(dict(form.params.submit('submit').list), params)
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        assert 'Registration' not in self.response.body
        assert 'Thank you for registering' in self.response.body
        # check that there are no further actions needed
        assert 'You may now login with your username' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
