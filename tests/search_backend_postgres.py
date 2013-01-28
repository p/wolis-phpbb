from wolis.test_case import WolisTestCase

class SearchBackendPostgresTest(WolisTestCase):
    def test_set_search_backend(self):
        self.login('morpheus', 'morpheus')
        self.acp_login('morpheus', 'morpheus')
        
        self.change_acp_knob(
            link_text='Search settings',
            check_page_text='Here you can define what search backend will be used',
            name='search_type',
            value='phpbb_search_fulltext_postgres',
        )

if __name__ == '__main__':
    import unittest
    unittest.main()
