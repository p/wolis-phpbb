import owebunit
import utils
from wolis_test_case import WolisTestCase

class InstallTestCase(WolisTestCase):
    def test_install(self):
        self.get('/')
        self.assert_redirected_to_uri('/install/index.php')
        
        self.follow_redirect()
        self.assert_status(200)
        
        # clicking on install link
        self.get('/install/index.php?mode=install&language=en')
        self.assert_status(200)
        
        assert 'Welcome to Installation' in self.response.body
        
        # first form is language selector
        assert len(self.response.forms) == 2
        
        form = self.response.forms[1]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'Test again' not in self.response.body
        assert 'Start install' in self.response.body
        
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'MySQL with MySQLi Extension' in self.response.body
        
        db_params = {
            'dbms': 'mysqli',
            'host': 'localhost',
            'dbport': '',
            'dbname': 'morpheus',
            'dbuser': 'root',
            'dbpasswd': '',
            'table_prefix': 'phpbb_',
        }
        
        form = self.response.forms[0]
        params = owebunit.extend_params(form.params.list, db_params)
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        assert 'Could not connect to the database' not in self.response.body
        assert 'Successful connection' in self.response.body
        
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'Administrator configuration' in self.response.body
        
        admin_params = {
            'admin_name': 'morpheus',
            'admin_pass1': 'morpheus',
            'admin_pass2': 'morpheus',
            'board_email': 'morpheus@localhost.test',
        }
        
        form = self.response.forms[0]
        params = owebunit.extend_params(form.params.list, admin_params)
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        
        assert 'Tests passed' in self.response.body
        
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'The configuration file has been written' in self.response.body
        
        assert len(self.response.forms) == 1
        form = self.response.forms[0]
        
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'The settings on this page are only necessary' in self.response.body
        
        # it's a giant form that we don't care for, just submit it
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'Proceed to the next screen to finish installing' in self.response.body
        
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'You have successfully installed' in self.response.body
        
        # have to submit this form also
        
        form = self.response.forms[0]
        self.post(form.computed_action, body=form.params.list)
        self.assert_status(200)
        
        assert 'Send statistical information' in self.response.body
        
        self._enable_debug()
    
    def _enable_debug(self):
        config_path = '/var/www/func/config.php'
        utils.sudo_chmod(config_path, 0664)
        with open(config_path) as f:
            config = f.read()
        config += "\n@define('DEBUG', true);\n@define('DEBUG_EXTRA', true);\n"
        with open(config_path, 'w') as f:
            f.write(config)

if __name__ == '__main__':
    import unittest
    unittest.main()
