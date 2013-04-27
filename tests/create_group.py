import webracer
from wolis import utils
from wolis.test_case import WolisTestCase

class CreateGroupTestCase(WolisTestCase):
    def test_create_group(self):
        self.login_and_nav()
        
        form = self.response.form(id='acp_groups')
        elements = form.elements.mutable
        elements.set_value('group_name', 'testgroup1')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Group details' in self.response.body
        
        form = self.response.form(id='settings')
        self.check_form_key_delay()
        self.post(form.computed_action, body=form.elements.params.list)
        self.assert_successish()
        
        assert 'Group has been created successfully' in self.response.body
    
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
        
        url = self.response.urljoin(self.link_href_by_text('Manage groups'))
        assert 'i=acp_groups' in url
        assert 'mode=manage' in url
        self.get(url)

if __name__ == '__main__':
    import unittest
    unittest.main()
