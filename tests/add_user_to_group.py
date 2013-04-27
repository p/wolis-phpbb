import webracer
from wolis import utils
from wolis.test_case import WolisTestCase
import lxml.etree

class AddUserToGroupTestCase(WolisTestCase):
    def test_add_user_to_group(self):
        username = 'prune2'
        group_name = 'testgroup1'
        
        self.login_and_nav()
        
        form = self.response.form(id='select_user')
        elements = form.elements.mutable
        elements.set_value('username', username)
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'User administration :: %s' % username in self.response.body
        
        form = self.response.form(id='mode_select')
        elements = form.elements.mutable
        elements.set_value('mode', 'groups')
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'Add user to group' in self.response.body
        
        doc = self.response.lxml_etree
        elt = webracer.utils.xpath_first_check(doc, '//form[@id="user_groups"]/table')
        html = lxml.etree.tostring(elt)
        assert group_name not in html
        
        form = self.response.form(id='user_groups')
        elements = form.elements.mutable
        doc = self.response.lxml_etree
        elt = webracer.utils.xpath_first_check(doc, '//option[text()="%s"]' % group_name)
        elements.set_value('g', elt.attrib['value'])
        self.check_form_key_delay()
        self.post(form.computed_action, body=elements.params.list)
        self.assert_successish()
        
        assert 'User defined groups user is a member of' in self.response.body
        doc = self.response.lxml_etree
        elt = webracer.utils.xpath_first_check(doc, '//form[@id="user_groups"]/table')
        html = lxml.etree.tostring(elt)
        assert group_name in html
    
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

if __name__ == '__main__':
    import unittest
    unittest.main()
