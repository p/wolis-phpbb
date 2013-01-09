import owebunit
import re
from wolis.test_case import WolisTestCase

# XXX enables an unspecified captcha, on my machine this happens to be nogd

class EnableCaptchaTestCase(WolisTestCase):
    def test_enable_captcha(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        self.change_acp_knob(
            link_text='Spambot countermeasures',
            check_page_text='Enable spambot countermeasures',
            name='enable_confirm',
            value='1',
        )

if __name__ == '__main__':
    import unittest
    unittest.main()
