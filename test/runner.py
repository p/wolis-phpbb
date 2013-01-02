import optparse
import os
import os.path
import subprocess
import utils
import db

test_root = '/var/www/func'
src = '/home/pie/apps/phpbb'
state_file_path = os.path.join(test_root, '.state')

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
        
        utils.rsync(os.path.join(src, 'phpBB/'), test_root, not self.resume)
            
        subprocess.call(['chmod', '-R', 'o+w', test_root])
        
        if not self.resume:
            self.drop_database()
            self.create_database()
        
        responses_dir = os.path.join(test_root, 'responses')
        if not os.path.exists(responses_dir):
            os.mkdir(responses_dir)
        
        flavor = self.detect_flavor()
        print('%s detected' % flavor)
        os.environ['FLAVOR'] = flavor
        
        import unittest
        
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
            if self.resume and self.passed_checkpoint(test):
                continue
            
            print('Testing %s' % test)
            parent = __import__('test.' + test)
            module = getattr(parent, test)
            # NB: exit=False is 2.7+
            result = unittest.main(module, exit=False).result
            if not result.wasSuccessful():
                exit(4)
            
            self.checkpoint(test)
        
        if os.path.exists(state_file_path):
            os.unlink(state_file_path)
    
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
