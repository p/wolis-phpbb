import os
import os.path
from wolis import utils
from wolis.test_case import WolisTestCase

class CreateSchemaFilesTestCase(WolisTestCase):
    def test_create_schema_files(self):
        script_path = utils.our_script_path('create-schema-files')
        src = self.conf.src_path
        work_dir = os.path.join(self.conf.test_root, 'repotest')
        if not os.path.exists(work_dir):
            os.mkdir(work_dir)
        os.chmod(work_dir, 0o777)
        
        utils.run((self.conf.php_cmd_prefix or []) + [script_path, src, work_dir])

if __name__ == '__main__':
    import unittest
    unittest.main()
