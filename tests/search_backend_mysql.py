from wolis.test_case import WolisTestCase
from wolis import utils

class SearchBackendMysqlTest(WolisTestCase):
    @utils.restrict_database('mysql*')
    @utils.restrict_phpbb_version('>=3.1.0')
    def test_set_search_backend(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        self.change_acp_knob(
            link_text='Search settings',
            check_page_text='Here you can define what search backend will be used',
            name='config[search_type]',
            value='phpbb_search_fulltext_mysql',
            confirm=True,
        )

if __name__ == '__main__':
    import unittest
    unittest.main()
