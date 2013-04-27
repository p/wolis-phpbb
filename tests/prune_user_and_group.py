import webracer
from wolis import utils
from wolis.test_case import WolisTestCase

# http://tracker.phpbb.com/browse/PHPBB3-11237
# requires selecting both user and a group, at the time of this writing
# selecting group only failed to find any users to prune

class PruneUserAndGroupTestCase(WolisTestCase):
    def test_prune_group(self):
        username = 'prune1'
        group_name = 'testgroup1'
        
        self.login_and_nav()
        
        db = utils.current.db or utils.instantiate_db(self.conf)
        with db.cursor() as c:
            c.execute('select user_id from phpbb_users where username=%s',
                (username,))
            row = c.fetchone()
            assert row is not None
        
        form = self.response.form()
        elements = form.elements.mutable
        elements.set_value('username', username)
        doc = self.response.lxml_etree
        elt = webracer.utils.xpath_first_check(doc, '//option[text()="%s"]' % group_name)
        elements.set_value('group_id', elt.attrib['value'])
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Users to be pruned' in self.response.body
        assert username in self.response.body
        
        self.submit_confirm_form()
        
        #assert 'The selected users have been deactivated successfully' in self.response.body
        assert 'The selected users have been deleted successfully' in self.response.body
        
        with db.cursor() as c:
            c.execute('select user_id from phpbb_users where username=%s',
                (username,))
            row = c.fetchone()
            assert row is None
    
    def login_and_nav(self):
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

if __name__ == '__main__':
    import unittest
    unittest.main()
