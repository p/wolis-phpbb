import webracer
from wolis import utils
from wolis.test_case import WolisTestCase

class PruneTestCase(WolisTestCase):
    def test_prune_one_user(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        start_url = '/adm/index.php'
        self.get_with_sid(start_url)
        self.assert_successish()
        
        assert 'Board statistics' in self.response.body
        
        url = self.response.urljoin(self.link_href_by_acp_tab_title('Users and Groups'))
        self.get(url)
        self.assert_successish()
        
        url = self.response.urljoin(self.link_href_by_text('Prune users'))
        assert 'i=acp_prune' in url
        self.get(url)
        
        db = utils.current.db or utils.instantiate_db(self.conf)
        with db.cursor() as c:
            c.execute('select user_id from phpbb_users where username=%s',
                ('prune1',))
            row = c.fetchone()
            assert row is not None
        
        form = self.response.form()
        elements = form.elements.mutable
        elements.set_value('username', 'prune1')
        elements.set_value('action', 'delete')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Users to be pruned' in self.response.body
        assert 'prune1' in self.response.body
        
        self.submit_confirm_form()
        
        #assert 'The selected users have been deactivated successfully' in self.response.body
        assert 'The selected users have been deleted successfully' in self.response.body
        
        with db.cursor() as c:
            c.execute('select user_id from phpbb_users where username=%s',
                ('prune1',))
            row = c.fetchone()
            assert row is None

if __name__ == '__main__':
    import unittest
    unittest.main()
