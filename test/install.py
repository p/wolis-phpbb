import owebunit
import urlparse

class InstallTestCase(owebunit.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(InstallTestCase, self).__init__(*args, **kwargs)
        self.config.host = 'http://func'
    
    def test_simple(self):
        self.get('/')
        self.assert_redirected_to_uri('/install/index.php')
        
        self.get('/install/index.php?mode=install&language=en')
        self.assert_status(200)
        
        self.get('/install/index.php?mode=install&sub=requirements&language=en')
        self.assert_status(200)
        
        assert 'Test again' not in self.response.body
        assert 'Start install' in self.response.body
        
        self.get('/install/index.php?mode=install&sub=database&language=en&')
        self.assert_status(200)
        
        assert 'MySQL with MySQLi Extension' in self.response.body
        
        params = {
            'dbms': 'mysqli',
            'host': 'localhost',
            'dbport': '',
            'dbname': 'morpheus',
            'dbuser': 'root',
            'dbpasswd': '',
        }
        
        db_params = owebunit.urlencode_utf8(params) + '&'
        params = db_params + 'mode=install&sub=database&language=en&table_prefix=phpbb_&testdb=true'
        self.post('/install/index.php', body=params)
        self.assert_status(200)
        
        assert 'Could not connect to the database' not in self.response.body
        assert 'Successful connection' in self.response.body
        
        params = db_params + 'language=en&table_prefix=phpbb_'
        self.post('/install/index.php?mode=install&sub=administrator', body=params)
        self.assert_status(200)
        
        assert 'Administrator configuration' in self.response.body
        
        admin_params = {
            'admin_name': 'morpheus',
            'admin_pass1': 'morpheus',
            'admin_pass2': 'morpheus',
            'board_email': 'morpheus@localhost.test',
        }
        
        admin_params = owebunit.urlencode_utf8(admin_params) + '&'
        params = db_params + admin_params + 'mode=install&sub=administrator&check=true&default_lang=en&language=en&table_prefix=phpbb_'
        url = '/install/index.php'
        self.post(url, body=params)
        self.assert_status(200)
        
        assert 'Tests passed' in self.response.body
        
        form = self.response.forms[0]
        url = urlparse.urljoin(url, form.computed_action)
        self.post(url, body=form.params_list)
        self.assert_status(200)
        
        assert 'The configuration file has been written' in self.response.body
        
        assert len(self.response.forms) == 1
        form = self.response.forms[0]
        
        url = urlparse.urljoin(url, form.computed_action)
        self.post(url, body=form.params_list)
        self.assert_status(200)
        
        assert 'The settings on this page are only necessary' in self.response.body
        
        # it's a giant form that we don't care for, just submit it
        form = self.response.forms[0]
        url = urlparse.urljoin(url, form.computed_action)
        self.post(url, body=form.params_list)
        self.assert_status(200)
        
        assert 'Proceed to the next screen to finish installing' in self.response.body
        
        form = self.response.forms[0]
        url = urlparse.urljoin(url, form.computed_action)
        self.post(url, body=form.params_list)
        self.assert_status(200)
        
        assert 'You have successfully installed' in self.response.body
        
        # have to submit this form also
        
        form = self.response.forms[0]
        url = urlparse.urljoin(url, form.computed_action)
        self.post(url, body=form.params_list)
        self.assert_status(200)
        
        assert 'Send statistical information' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
