import optparse
import os
import os.path
import subprocess
import sys
import unittest
from . import utils
from . import db
from . import config

class Runner(object):
    def __init__(self):
        # command line options
        self.resume = False
        self.dbms = None
        
        self.conf = config.Config()
    
    def instantiate_db(self):
        driver = self.requested_dbms
        class_name = driver[0].upper() + driver[1:] + 'Db'
        cls = getattr(db, class_name)
        self.db = cls()
    
    @property
    def requested_dbms(self):
        return self.dbms or self.conf.db['driver']
    
    def parse_options(self):
        parser = optparse.OptionParser()
        parser.add_option('-r', '--resume', help='resume previous run',
            action='store_true', dest='resume')
        parser.add_option('-d', '--db', help='Use specified database driver',
            action='store', dest='db')
        options, args = parser.parse_args()
        if options.resume:
            self.resume = True
        self.dbms = options.db
        if len(args) > 0:
            parser.print_help()
            exit(4)
        # clear argv, as otherwise unittest tries to process it
        sys.argv[1:] = []
    
    def run(self):
        self.parse_options()
        self.instantiate_db()
        self.create_casper_config_file()
        self.copy_tree_under_test(not self.resume)
        
        if not self.resume:
            self.drop_database()
            self.create_database()
        
        flavor = self.detect_flavor()
        print('%s detected' % flavor)
        os.environ['FLAVOR'] = flavor
        
        os.environ['DBMS'] = self.requested_dbms
        
        tests = [
            'lint_js',
            'install',
            'login_without_cookies',
            'login',
            'acp_login',
            'acp_knobs',
            'view_index',
            'casper.view_index',
            'casper.registration_agreement',
            'casper.registration_tz_selection',
            'register',
            'report_post',
            'install_subsilver',
            # Cannot uninstall default style
            #'set_subsilver_default',
            'uninstall_subsilver',
            'update',
        ]
        for test in tests:
            self.run_test('pass1', test)
        
        checkpoint_name = 'pass2prep'
        if not self.resume or not self.passed_checkpoint(checkpoint_name):
            self.update_baseline_repo()
            utils.git_in_dir(self.conf.baseline_repo_path, 'checkout', 'release-3.0.11')
            utils.rsync(os.path.join(self.conf.baseline_repo_path, 'phpBB/'), self.conf.test_root_phpbb, True)
            self.post_copy_tree()
            self.drop_database()
            self.create_database()
            self.checkpoint(checkpoint_name)
        
        os.environ['FLAVOR'] = 'olympus'
        self.run_test('pass2', 'install')
        
        self.copy_tree_under_test(True, exclude='/config.php')
        
        os.environ['FLAVOR'] = flavor
        self.run_test('pass2', 'update')
        
        if os.path.exists(self.conf.state_file_path):
            os.unlink(self.conf.state_file_path)
    
    def copy_tree_under_test(self, delete=False, exclude=None):
        utils.rsync(os.path.join(self.conf.src, 'phpBB/'), self.conf.test_root_phpbb,
            delete=delete, exclude=exclude)
        
        self.post_copy_tree()
    
    def post_copy_tree(self):
        subprocess.call(['chmod', '-R', 'o+w', self.conf.test_root_phpbb])
        
        if not os.path.exists(self.conf.responses_dir):
            os.mkdir(self.conf.responses_dir)
    
    def run_test(self, prefix, name):
        checkpoint_name = '%s.%s' % (prefix, name)
        if self.resume and self.passed_checkpoint(checkpoint_name):
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
        # NB: exit=False is 2.7+
        result = unittest.main(module, exit=False).result
        if not result.wasSuccessful():
            exit(4)
    
    def run_casper_test(self, name):
        test_path = os.path.join(os.path.dirname(__file__), '../frontend', name + '.coffee')
        casper_config_path = os.path.join(self.conf.test_root, 'gen', 'default.js')
        utils.casper(test_path, pre=casper_config_path)
    
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
        if not os.path.exists(self.conf.baseline_repo_path):
            try:
                subprocess.check_call(['git', 'init', self.conf.baseline_repo_path])
                utils.git_in_dir(self.conf.baseline_repo_path, 'remote', 'add', 'upstream', 'git://github.com/phpbb/phpbb3.git', '-f')
            except:
                self.delete_baseline_repo_silently()
                raise
        
        #utils.git_in_dir(baseline_repo_path, 'fetch', 'upstream')
    
    def delete_baseline_repo_silently(self):
        if os.path.exists(baseline_repo_path):
            try:
                shutil.rmtree(baseline_repo_path)
            except:
                pass
    
    def drop_database(self):
        self.db.drop_database('wolis')
    
    def create_database(self):
        self.db.create_database('wolis')
    
    def detect_flavor(self):
        if os.path.exists(os.path.join(self.conf.test_root, 'includes/extension/manager.php')):
            flavor = 'ascraeus'
        else:
            flavor = 'olympus'
        return flavor
    
    def create_casper_config_file(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/default.yml')
        json = utils.yaml_to_json(input_file=config_path)
        json = '''
            global.wolisconfig = %s;
            casper.test.done();
        ''' % json
        output_dir = os.path.join(self.conf.test_root, 'gen')
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_path = os.path.join(output_dir, 'default.js')
        with open(output_path, 'wb') as f:
            f.write(json)
