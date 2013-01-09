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
        
        self.change_acp_knob(
            link_text='Board settings',
            check_page_text='Here you can determine the basic operation of your board',
            name='config[board_timezone]',
            value='Antarctica/Macquarie',
        )
        
        with self.session() as s:
            s.get('/')
            self.assert_successish(s)
            
            assert re.search(r'All times are.*GMT\+11:00', s.response.body)

if __name__ == '__main__':
    import unittest
    unittest.main()
