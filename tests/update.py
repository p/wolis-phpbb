import owebunit
from wolis import utils
from wolis.test_case import WolisTestCase

class UpdateTestCase(WolisTestCase):
    def setup(self):
        super(UpdateTestCase, self).setup()
        
        #self.clear_cache()
    
    def test_update(self):
        self.get('/install/database_update.php')
        self.assert_successish()

if __name__ == '__main__':
    import unittest
    unittest.main()
