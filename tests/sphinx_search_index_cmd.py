# -*- coding: utf-8 -*-

from wolis.test_case import WolisTestCase
from wolis import utils

class SphinxSearchIndexCmdTest(WolisTestCase):
    def test_create_index(self):
        with open(self.conf.sphinx_id_path) as f:
            sphinx_id = f.read()
        
        cmd = cmd = self.conf.sphinx_cmd_prefix or []
        utils.run(cmd + ['indexer', '--config', self.conf.sphinx_config_path,
            'index_phpbb_%s_main' % sphinx_id])
        utils.run(cmd + ['indexer', '--config', self.conf.sphinx_config_path,
            'index_phpbb_%s_delta' % sphinx_id])

if __name__ == '__main__':
    import unittest
    unittest.main()
