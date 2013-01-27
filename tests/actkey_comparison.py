from wolis.test_case import WolisTestCase
from wolis import utils

class ActkeyComparisonTest(WolisTestCase):
    def test_valid_actkey(self):
        url = '/ucp.php?mode=sendpassword'
        self.get(url)
        self.assert_successish()
        
        form = self.response.form(id='remind')
        elements = form.elements.mutable
        elements.set_value('username', 'morpheus')
        elements.set_value('email', 'morpheus@localhost.test')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'A new password was sent to your registered email address.'
        
        db = utils.current.db or utils.instantiate_db(self.conf)
        with db.cursor() as c:
            c.execute('select user_id, user_actkey from phpbb_users where username=%s',
                ('morpheus',))
            uid, actkey = c.fetchone()
        
        self.get('/ucp.php?mode=activate&u=%s&k=%s' % (uid, actkey))
        self.assert_successish()
        
        assert 'You have already activated your account.' not in self.response.body
        assert 'Your new password has been activated.' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
