import os
import tempfile
from wolis import utils
from wolis.test_case import WolisTestCase

class LintJsTestCase(WolisTestCase):
    def test_lint_js(self):
        prefix = self.conf.test_root_phpbb
        jshint_config_path = os.path.join(os.path.dirname(__file__), '../config/jshint.syntax.yaml')
        with tempfile.NamedTemporaryFile() as jshint_config_f:
            utils.yaml_to_json(input_file=jshint_config_path,
                output_file=jshint_config_f)
            jshint_config_f.flush()
            # since we run jshint under a different user account,
            # adjust permissions to be more open
            os.chmod(jshint_config_f.name, 0o644)
            if not prefix.endswith('/'):
                prefix += '/'
            for root, dirs, files in os.walk(self.conf.test_root_phpbb):
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    if file.endswith('.js'):
                        # test_root should be absolute
                        path = os.path.join(root, file)
                        print 'Linting %s' % path
                        utils.sudo_rvm(['uglifyjs', '-o', '/dev/null', path])
                        
                        # use a temporary file in case there is a lot of output
                        with tempfile.TemporaryFile() as f:
                            utils.sudo_rvm(['jshint', '--config', jshint_config_f.name, path], no_check=True, stdout=f)
                            f.seek(0)
                            for line in f.readlines():
                                if 'Extra comma.' in line:
                                    relative_path = path[len(prefix):]
                                    msg = "jshint reports trailing comma in %s:\n%s" % (relative_path, line.strip())
                                    self.fail(msg)

if __name__ == '__main__':
    import unittest
    unittest.main()
