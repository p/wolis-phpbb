import owebunit
from wolis.test_case import WolisTestCase

class ViewIndexTestCase(WolisTestCase):
    def test_view_index(self):
        self.get('/index.php')
        self.assert_successish()
        
        assert 'Index page' in self.response.body

if __name__ == '__main__':
    import unittest
    unittest.main()
