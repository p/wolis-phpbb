import os
import webracer
from wolis import utils
from wolis.test_case import WolisTestCase

class InstallTestCase(WolisTestCase):
    def test_install(self):
        self.get('/')
        self.assert_redirected_to_uri('/install/index.php')
        
        self.follow_redirect()
        self.assert_successish()
        
        # clicking on install link
        self.get('/install/index.php?mode=install&language=en')
        self.assert_successish()
        
        assert 'Welcome to Installation' in self.response.body
        
        form = self.response.form(id='install_install')
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'Test again' not in self.response.body
        assert 'Start install' in self.response.body
        
        form = self.response.form()
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'MySQL with MySQLi Extension' in self.response.body
        
        dbms = os.environ.get('DBMS') or self.conf.db.driver
        db_params = {
            'dbms': dbms,
            'table_prefix': self.conf.db.table_prefix,
        }
        attr_map = dict(host='host', port='dbport', dbname='dbname',
            user='dbuser', password='dbpasswd')
        attrs = getattr(self.conf, dbms)
        for fk in attr_map:
            lk = attr_map[fk]
            if fk in attrs:
                db_params[lk] = attrs.get(fk)
        
        form = self.response.form()
        params = webracer.extend_params(form.params.list, db_params)
        self.post(form.computed_action, body=params)
        self.assert_successish()
        
        assert 'Could not connect to the database' not in self.response.body
        assert 'Successful connection' in self.response.body
        
        form = self.response.form()
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'Administrator configuration' in self.response.body
        
        admin_params = {
            'admin_name': 'morpheus',
            'admin_pass1': 'morpheus',
            'admin_pass2': 'morpheus',
            'board_email': 'morpheus@localhost.test',
        }
        
        if self.phpbb_version < (3, 1, 0):
            admin_params['board_email1'] = admin_params['board_email']
            admin_params['board_email2'] = admin_params['board_email']
        
        form = self.response.form()
        params = webracer.extend_params(form.params.list, admin_params)
        self.post(form.computed_action, body=params)
        self.assert_successish()
        
        assert 'Tests passed' in self.response.body
        
        form = self.response.form()
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'The configuration file has been written' in self.response.body
        
        form = self.response.form()
        
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'The settings on this page are only necessary' in self.response.body
        
        # it's a giant form that we don't care for, just submit it
        form = self.response.form()
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'Proceed to the next screen to finish installing' in self.response.body
        
        form = self.response.form()
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'You have successfully installed' in self.response.body
        
        # have to submit this form also
        
        form = self.response.form()
        self.post(form.computed_action, body=form.params.list)
        self.assert_successish()
        
        assert 'Send statistical information' in self.response.body
        
        self._enable_debug()
    
    def _enable_debug(self):
        config_path = os.path.join(self.conf.test_root_phpbb, 'config.php')
        if self.conf.php_cmd_prefix:
            utils.run(self.conf.php_cmd_prefix + ['chmod', '0644', config_path])
        else:
            os.chmod(config_path, 0o644)
        with open(config_path) as f:
            config = f.read()
        config += "\n@define('DEBUG', true);\n@define('DEBUG_EXTRA', true);\n"
        # if config file was created by php, it will have php as the owner
        # and therefore we won't be able to write to it with 644 mode.
        # but we can unlink it because we own the directory it is in.
        # note that there is an obvious race here, but it should not matter.
        if os.path.exists(config_path):
            os.unlink(config_path)
        with open(config_path, 'w') as f:
            f.write(config)

if __name__ == '__main__':
    import unittest
    unittest.main()
