import optparse
import os
import os.path
import subprocess
import unittest
import utils
import db

test_root = '/var/www/func'
src = '/home/pie/apps/phpbb'
state_file_path = os.path.join(test_root, '.state')
baseline_repo_path = os.path.join(test_root, 'repo')
test_root_phpbb = os.path.join(test_root, 'phpbb')
responses_dir = os.path.join(test_root_phpbb, 'responses')

class Runner(object):
    def __init__(self):
        self.resume = False
        self.db = db.MysqlDb()
    
    def parse_options(self):
        parser = optparse.OptionParser()
        parser.add_option('-c', '--continue', help='continue previous run',
            action='store_true', dest='resume')
        options, args = parser.parse_args()
        if options.resume:
            self.resume = True
        if len(args) > 0:
            parser.print_help()
            exit(4)
    
    def run(self):
        self.parse_options()
        self.copy_tree_under_test(not self.resume)
        
        if not self.resume:
            self.drop_database()
            self.create_database()
        
        flavor = self.detect_flavor()
        print('%s detected' % flavor)
        os.environ['FLAVOR'] = flavor
        
        tests = [
            'install',
            'login_without_cookies',
            'login',
            'acp_login',
            'acp_knobs',
            'register',
            'update',
        ]
        for test in tests:
            self.run_test('pass1', test)
        
        checkpoint_name = 'pass2prep'
        if not self.resume or not self.passed_checkpoint(checkpoint_name):
            self.update_baseline_repo()
            utils.git_in_dir(baseline_repo_path, 'checkout', 'release-3.0.11')
            utils.rsync(os.path.join(baseline_repo_path, 'phpBB/'), test_root_phpbb, True)
            self.post_copy_tree()
            self.drop_database()
            self.create_database()
            self.checkpoint(checkpoint_name)
        
        os.environ['FLAVOR'] = 'olympus'
        self.run_test('pass2', 'install')
        
        self.copy_tree_under_test(True, exclude='/config.php')
        
        os.environ['FLAVOR'] = flavor
        self.run_test('pass2', 'update')
        
        if os.path.exists(state_file_path):
            os.unlink(state_file_path)
    
    def copy_tree_under_test(self, delete=False, exclude=None):
        utils.rsync(os.path.join(src, 'phpBB/'), test_root_phpbb,
            delete=delete, exclude=exclude)
        
        self.post_copy_tree()
    
    def post_copy_tree(self):
        subprocess.call(['chmod', '-R', 'o+w', test_root_phpbb])
        
        if not os.path.exists(responses_dir):
            os.mkdir(responses_dir)
    
    def run_test(self, prefix, name):
        checkpoint_name = '%s.%s' % (prefix, name)
        if self.resume and self.passed_checkpoint(checkpoint_name):
            return
        
        print('Testing %s.%s' % (prefix, name))
        parent = __import__('test.' + name)
        module = getattr(parent, name)
        # NB: exit=False is 2.7+
        result = unittest.main(module, exit=False).result
        if not result.wasSuccessful():
            exit(4)
        
        self.checkpoint(checkpoint_name)
    
    def clear_state(self):
        if os.path.exists(state_file_path):
            os.unlink(state_file_path)
    
    def checkpoint(self, name):
        with open(state_file_path, 'ab') as f:
            f.write(name + "\n")
    
    def passed_checkpoint(self, name):
        if not os.path.exists(state_file_path):
            return False
        with open(state_file_path, 'rb') as f:
            if name + "\n" in f.readlines():
                return True
        return False
    
    def update_baseline_repo(self):
        if not os.path.exists(baseline_repo_path):
            try:
                subprocess.check_call(['git', 'init', baseline_repo_path])
                utils.git_in_dir(baseline_repo_path, 'remote', 'add', 'upstream', 'git://github.com/phpbb/phpbb3.git', '-f')
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
        if os.path.exists(os.path.join(test_root, 'includes/extension/manager.php')):
            flavor = 'ascraeus'
        else:
            flavor = 'olympus'
        return flavor
