import webracer
from wolis import utils
from wolis.test_case import WolisTestCase

class RegisterForPruningTestCase(WolisTestCase):
    def test_register(self):
        for i in [1, 2]:
            print('Registering user %d' % i)
            
            self.get('/ucp.php?mode=register')
            self.assert_successish()
            
            assert 'Registration' in self.response.body
            
            form = self.response.form(id='agreement')
            elements = form.elements.mutable
            elements.submit('agreed')
            self.post(form.computed_action, body=elements.params.list)
            self.assert_successish()
            
            assert 'Username:' in self.response.body
            
            form = self.response.form(id='register')
            # for repeated runs
            suffix = self.random_suffix()
            params = {
                'username': 'prune%d' % i,
                'new_password': 'test42',
                'password_confirm': 'test42',
                'email': 'foo%d@bar.local' % i,
                'lang': 'en',
                'tz': 'UTC',
                'confirm_id': '',
                'confirm_code': '',
            }
            
            if self.phpbb_version < (3, 1, 0):
                params['email_confirm'] = params['email']
            
            self.check_form_key_delay()
            
            elements = form.elements.mutable
            elements.submit('submit')
            params = webracer.extend_params(elements.params.dict, params)
            self.post(form.computed_action, body=params)
            self.assert_successish()
            
            assert 'Registration' not in self.response.body
            assert 'Thank you for registering' in self.response.body
            # check that there are no further actions needed
            assert 'You may now login with your username' in self.response.body
            
            self.logout()

if __name__ == '__main__':
    import unittest
    unittest.main()
