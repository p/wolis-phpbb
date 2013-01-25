import re
import optparse
import os
import os.path
import subprocess
import sys
import unittest
from . import utils
from . import db
from . import config
from . import test_case

class Runner(object):
    def __init__(self):
        # command line options
        self.resume = False
        self.dbms = None
        self.requested_tests = None
        self.config_file_path = None
        self.conf = None
    
    def instantiate_db(self):
        driver = self.requested_dbms
        class_name = driver[0].upper() + driver[1:] + 'Db'
        cls = getattr(db, class_name)
        self.db = cls()
    
    @property
    def requested_dbms(self):
        return self.dbms or self.conf.db.driver
    
    def parse_options(self):
        parser = optparse.OptionParser()
        parser.add_option('-r', '--resume', help='resume previous run',
            action='store_true', dest='resume')
        parser.add_option('-c', '--config', help='Path to configuration file',
            action='store', dest='config')
        parser.add_option('-d', '--db', help='Use specified database driver',
            action='store', dest='db')
        options, args = parser.parse_args()
        if options.config:
            print('Using %s' % options.config)
            self.config_file_path = options.config
        else:
            self.config_file_path = os.path.join(os.path.dirname(__file__), '../config/default.yaml')
        self.conf = config.Config(self.config_file_path)
        if options.resume:
            self.resume = True
        self.dbms = options.db
        if args:
            self.requested_tests = args
        utils.current.config = self.conf
    
    def run(self):
        self.parse_options()
        self.instantiate_db()
        self.casper_config_path = self.create_casper_config_file()
        self.copy_tree_under_test(not self.resume)
        self.delete_old_responses()
        # set to world write as casper writes there
        os.chmod(self.conf.responses_dir, 0o777)
        
        if not self.resume:
            self.drop_database()
            self.create_database()
        
        print('%s detected' % utils.current.phpbb_version)
        
        os.environ['DBMS'] = self.requested_dbms
        
        tests = [
            'lint_js',
            'create_schema_files',
            'install',
            'login_without_cookies',
            'login',
            'acp_login',
            'acp_knobs',
            'admin_log',
            'empty_logs',
            'view_index',
            'casper.view_index',
            'casper.registration_agreement',
            'casper.registration_tz_selection',
            'casper.login',
            'casper.login_helper',
            'casper.topic_bookmarking',
            'register',
            'report_post',
            'install_subsilver',
            # Cannot uninstall default style
            #'set_subsilver_default',
            'uninstall_subsilver',
            'enable_captcha',
            'captcha_nogd',
            'update',
        ]
        for test in tests:
            self.run_test('pass1', test)
        
        checkpoint_name = 'pass2prep'
        if not self.resume or not self.passed_checkpoint(checkpoint_name):
            self.update_baseline_repo()
            utils.git_in_dir(self.conf.baseline_repo_path, 'checkout', '-q', 'release-3.0.11')
            utils.rsync(os.path.join(self.conf.baseline_repo_path, 'phpBB/'), self.conf.test_root_phpbb, True)
            self.post_copy_tree()
            self.drop_database()
            self.create_database()
            self.checkpoint(checkpoint_name)
        
        self.run_test('pass2', 'install')
        
        self.copy_tree_under_test(True, exclude='/config.php')
        
        self.run_test('pass2', 'update')
        
        if os.path.exists(self.conf.state_file_path):
            os.unlink(self.conf.state_file_path)
    
    def copy_tree_under_test(self, delete=False, exclude=None):
        if self.conf.src[0] == '/':
            utils.rsync(os.path.join(self.conf.src, 'phpBB/'),
                self.conf.test_root_phpbb,
                delete=delete, exclude=exclude)
        else:
            self.update_src_repo()
            utils.git_in_dir(self.conf.src_repo_path,
                'checkout', 'src/%s' % self.conf.src_branch)
            utils.rsync(os.path.join(self.conf.src_repo_path, 'phpBB/'),
                self.conf.test_root_phpbb,
                delete=delete, exclude=exclude)
        
        self.post_copy_tree()
    
    def delete_old_responses(self):
        dir = self.conf.responses_dir
        for file in os.listdir(dir):
            if file[0] == '.':
                continue
            
            os.unlink(os.path.join(dir, file))
    
    def post_copy_tree(self):
        subprocess.call(['chmod', '-R', 'o+w', self.conf.test_root_phpbb])
        
        if not os.path.exists(self.conf.responses_dir):
            os.mkdir(self.conf.responses_dir)
        
        utils.current.phpbb_version = utils.PhpbbVersion(self.conf)
        
        if self.conf.use_composer:
            # test_root_phpbb is only phpBB path of the repo and has no
            # composer.phar in it
            composer_path = os.path.join(self.conf.src_path, 'composer.phar')
            utils.run_in_dir(self.conf.test_root_phpbb,
                self.conf.php_cmd_prefix + ['php', composer_path, 'install', '--dev'])
    
    def run_test(self, prefix, name):
        checkpoint_name = '%s.%s' % (prefix, name)
        if self.resume and self.passed_checkpoint(checkpoint_name):
            return
        if self.requested_tests is not None:
            if checkpoint_name not in self.requested_tests:
                return
        
        print('Testing %s.%s' % (prefix, name))
        
        if '.' in name:
            method, name = name.split('.')
            if method == 'casper':
                self.run_casper_test(name)
            else:
                raise ValueError, 'Unsppported method: %s' % method
        else:
            self.run_python_test(name)
        
        self.checkpoint(checkpoint_name)
    
    def run_python_test(self, name):
        parent = __import__('tests.' + name)
        module = getattr(parent, name)
        try:
            # python 2.7
            test_loader = unittest.loader.defaultTestLoader
            test_runner = unittest.runner.TextTestRunner
        except AttributeError:
            # python 2.6
            test_loader = unittest.defaultTestLoader
            test_runner = unittest.TextTestRunner
        tests = test_loader.loadTestsFromModule(module)
        try:
            runner = test_runner(verbosity=1)
        except TypeError:
            # per unittest.main code
            runner = test_runner()
        result = runner.run(tests)
        if not result.wasSuccessful():
            exit(4)
    
    def run_casper_test(self, name):
        test_path = os.path.join(os.path.dirname(__file__), '../frontend', name + '.coffee')
        
        with open(test_path, 'r') as f:
            code = f.read()
            regexp = re.compile(r'^(?:(?:|\s+|\s*#[^\n]*)\n)*?(# (?:depends|after|phpbb_version):\n(?:#[^\n]*\n)*)\n', re.S)
            match = regexp.match(code)
            if not match:
                print("Test %s does not have meta information")
            else:
                meta = match.group(1)
                lines = meta.split("\n")
                from . import test_meta
                parser = test_meta.Parser()
                for line in lines:
                    if len(line) > 0:
                        assert line[0] == '#'
                    if len(line) > 1:
                        assert line[1] == ' '
                    line = line[2:]
                    parser.feed(line)
                if parser.phpbb_version:
                    for version in parser.phpbb_version:
                        if not utils.current.phpbb_version.matches(version):
                            print('Skipping test due to phpBB version constraint (%s)' % version)
                            return
        
        utils.casper(self.conf, test_path, pre=self.casper_config_path)
    
    def clear_state(self):
        if os.path.exists(self.conf.state_file_path):
            os.unlink(self.conf.state_file_path)
    
    def checkpoint(self, name):
        with open(self.conf.state_file_path, 'ab') as f:
            f.write(name + "\n")
    
    def passed_checkpoint(self, name):
        if not os.path.exists(self.conf.state_file_path):
            return False
        with open(self.conf.state_file_path, 'rb') as f:
            if name + "\n" in f.readlines():
                return True
        return False
    
    def update_baseline_repo(self):
        utils.clone_repo('git://github.com/phpbb/phpbb3.git',
            self.conf.baseline_repo_path, 'upstream')
    
    def update_src_repo(self):
        utils.clone_repo(self.conf.src,
            self.conf.src_repo_path, 'src')
    
    def drop_database(self):
        self.db.drop_database('wolis')
    
    def create_database(self):
        self.db.create_database('wolis')
    
    def create_casper_config_file(self):
        config_file_name = os.path.basename(self.config_file_path)
        json = utils.yaml_to_json(input_file=self.config_file_path)
        json = '''
            global.wolis = {};
            global.wolis.config = %s;
            casper.test.done();
        ''' % json
        output_dir = os.path.join(self.conf.test_root, 'gen')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_path = os.path.join(output_dir, config_file_name.replace('.yaml', '.js'))
        with open(output_path, 'wb') as f:
            f.write(json)
        return output_path
