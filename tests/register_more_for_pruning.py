import webracer
from wolis import utils
from wolis.test_case import WolisTestCase
from . import register_for_pruning

class RegisterMoreForPruningTestCase(register_for_pruning.RegisterForPruningTestCase):
    def test_register(self):
        self.do_register(2)

if __name__ == '__main__':
    import unittest
    unittest.main()
