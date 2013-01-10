import owebunit
import re
from wolis.test_case import WolisTestCase

class AcpKnobsTestCase(WolisTestCase):
    def test_disable_captcha(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        self.change_acp_knob(
            link_text='Spambot countermeasures',
            check_page_text='Enable spambot countermeasures',
            name='enable_confirm',
            value='0',
        )
    
    def test_disable_mx_check(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        self.change_acp_knob(
            link_text='Security settings',
            check_page_text='Here you are able to define session and login related settings',
            name='config[email_check_mx]',
            value='0',
        )
    
    def test_set_timezone(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        if self.phpbb_version < (3, 1, 0):
            # utc offset
            value = '11'
        else:
            # timezone name
            value = 'Antarctica/Macquarie'
        self.change_acp_knob(
            link_text='Board settings',
            check_page_text='Here you can determine the basic operation of your board',
            name='config[board_timezone]',
            value=value,
        )
        
        with self.session() as s:
            s.get('/')
            self.assert_successish(s)
            
            if self.phpbb_version < (3, 1, 0):
                search = r'All times are UTC \+ 11 hours'
            else:
                search = r'All times are.*GMT\+11:00'
            assert re.search(search, s.response.body)

if __name__ == '__main__':
    import unittest
    unittest.main()
