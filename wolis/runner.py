import re
import optparse
import os
import os.path
import subprocess
import sys
import unittest
from . import utils
from . import config
from . import test_case

class CoffeeFailError(StandardError):
    pass

class Runner(object):
    def __init__(self):
        # command line options
        self.resume = False
        self.dbms = None
        self.requested_tests = None
        self.branch = None
        self.config_file_path = None
        self.conf = None
    
    def instantiate_db(self):
        self.db = utils.instantiate_db(self.conf, self.actual_dbms)
        utils.current.dbms = self.actual_dbms
        utils.current.db = self.db
    
    @property
    def actual_dbms(self):
        return self.dbms or self.conf.db.driver
    
    def parse_options(self):
        parser = optparse.OptionParser()
        parser.add_option('-r', '--resume', help='resume previous run',
            action='store_true', dest='resume')
        parser.add_option('-c', '--config', help='Path to configuration file',
            action='store', dest='config')
        parser.add_option('-b', '--branch', help='Override branch for url sources',
            action='store', dest='branch')
        parser.add_option('-d', '--db', help='Use specified database driver',
            action='store', dest='db')
        options, args = parser.parse_args()
        if options.config:
            print('Using %s' % options.config)
            self.config_file_path = options.config
        else:
            self.config_file_path = os.path.join(os.path.dirname(__file__), '../config/default.yaml')
        self.conf = config.Config(self.config_file_path)
        if options.branch:
            self.branch = options.branch
        if options.resume:
            self.resume = True
        self.dbms = options.db
        if args:
            self.requested_tests = args
        utils.current.config = self.conf
    
    def run(self):
        self.parse_options()
        
        if not self.resume:
            self.clear_state()
        
        self.instantiate_db()
        self.casper_config_path = self.create_casper_config_file()
        self.copy_tree_under_test(not self.resume)
        self.delete_old_responses()
        # set to world write as casper writes there
        os.chmod(self.conf.responses_dir, 0o777)
        # and gen for coffeescript when compiling
        os.chmod(self.conf.gen_path, 0o777)
        
        print('%s detected' % utils.current.phpbb_version)
        
        os.environ['DBMS'] = self.actual_dbms
        
        tests = [
            'prep.drop_database',
            'prep.create_database',
            'python.lint_js',
            'python.create_schema_files',
            'python.install',
            'python.login_without_cookies',
            'python.login',
            'python.acp_login',
            'python.acp_knobs',
            'python.template_compile_race',
            'python.admin_log',
            'python.empty_logs',
            'python.view_index',
            'casper.view_index',
            'casper.registration_agreement',
            'casper.registration_tz_selection',
            'casper.login',
            'casper.login_helper',
            'casper.topic_bookmarking',
            'casper.acp_login',
            'casper.acp_login_helper',
            'python.register',
            'python.report_post',
            'python.post',
            'python.post_lots',
            'python.search',
            'python.search_pagination',
            'casper.delete_native_search_index',
            'python.search_verify_no_backends',
            'python.search_verify_no_results',
        ]
        self.run_tests('pass1', tests)
        
        if utils.current.phpbb_version >= (3, 1, 0):
            if utils.db_matches(self.actual_dbms, 'postgres'):
                tests = [
                    'casper.postgres_search_index',
                    'python.search_backend_postgres',
                    'python.search',
                    'python.search_pagination',
                ]
                self.run_tests('pass2', tests)
            elif utils.db_matches(self.actual_dbms, 'mysql*'):
                tests = [
                    'prep.switch_posts_to_myisam',
                    'casper.mysql_search_index',
                    'python.search_backend_mysql',
                    'python.search',
                    'python.search_pagination',
                ]
                self.run_tests('pass2', tests)
        
        tests = [
            'casper.create_native_search_index',
            'python.install_subsilver',
            # Cannot uninstall default style
            #'python.set_subsilver_default',
            'python.uninstall_subsilver',
            'python.enable_captcha',
            'python.captcha_nogd',
            'python.actkey_comparison',
            'python.update',
        ]
        self.run_tests('pass3', tests)
        
        tests = [
            'prep.copy_starting_tree_for_update',
            'prep.drop_database',
            'prep.create_database',
            'python.install',
            'prep.copy_tree_for_update',
            'python.update',
        ]
        self.run_tests('pass4', tests)
        
        self.clear_state()
    
    def copy_starting_tree_for_update(self):
        self.update_baseline_repo()
        utils.git_in_dir(self.conf.baseline_repo_path, 'checkout', '-q', 'release-3.0.11')
        
        if self.conf.use_composer:
            vendor_path = os.path.join(self.conf.test_root_phpbb, 'vendor')
            utils.run(self.conf.php_cmd_prefix + ['rm', '-rf', vendor_path])
        
        utils.rsync(os.path.join(self.conf.baseline_repo_path, 'phpBB/'), self.conf.test_root_phpbb, True)
        self.post_copy_tree(self.conf.baseline_repo_path)
    
    def copy_tree_for_update(self):
        self.copy_tree_under_test(True, exclude='/config.php')
    
    def delete_old_responses(self):
        dir = self.conf.responses_dir
        for file in os.listdir(dir):
            if file[0] == '.':
                continue
            
            os.unlink(os.path.join(dir, file))
    
    def copy_tree_under_test(self, delete=False, exclude=None):
        if self.conf.use_composer:
            vendor_path = os.path.join(self.conf.test_root_phpbb, 'vendor')
            utils.run(self.conf.php_cmd_prefix + ['rm', '-rf', vendor_path])
        
        if self.conf.src[0] == '/':
            src_path = self.conf.src
        else:
            self.update_src_repo()
            branch = self.branch or self.conf.src_branch
            utils.git_in_dir(self.conf.src_repo_path,
                'checkout', 'src/%s' % branch)
            src_path = self.conf.src_repo_path
        
        utils.rsync(os.path.join(src_path, 'phpBB/'),
            self.conf.test_root_phpbb,
            delete=delete, exclude=exclude)
        
        self.post_copy_tree(src_path)
    
    def post_copy_tree(self, src_path):
        subprocess.call(['chmod', '-R', 'o+w', self.conf.test_root_phpbb])
        
        if not os.path.exists(self.conf.responses_dir):
            os.mkdir(self.conf.responses_dir)
        
        utils.current.phpbb_version = utils.PhpbbVersion(self.conf)
        
        # 3.0.11 has no composer.json
        if self.conf.use_composer and os.path.exists(os.path.join(self.conf.test_root_phpbb, 'composer.json')):
            # test_root_phpbb is only phpBB path of the repo and has no
            # composer.phar in it
            composer_path = os.path.join(src_path, 'composer.phar')
            utils.run_in_dir(self.conf.test_root_phpbb,
                self.conf.php_cmd_prefix + ['php', composer_path, 'install', '--dev'])
    
    def run_tests(self, prefix, names):
        for name in names:
            self.run_test(prefix, name)
    
    def run_test(self, prefix, name):
        checkpoint_name = '%s.%s' % (prefix, name)
        if self.resume and self.passed_checkpoint(checkpoint_name):
            return
        if self.requested_tests is not None:
            if checkpoint_name not in self.requested_tests:
                return
        
        print('Testing %s.%s' % (prefix, name))
        
        assert '.' in name
        method, name = name.split('.')
        if method == 'prep':
            method = getattr(self, name)
            method()
        elif method == 'python':
            self.run_python_test(name)
        elif method == 'casper':
            self.run_casper_test(name)
        else:
            raise ValueError, 'Unsppported method: %s' % method
        
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
        utils.flush_streams()
        result = runner.run(tests)
        utils.flush_streams()
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
                            print('Skipping test %s due to phpBB version constraint (%s)' % (name, version))
                            return
                if parser.db:
                    if not utils.db_matches_list(self.actual_dbms, parser.db):
                        print('Skipping test %s due to database requirement (%s)' % (name, ', '.join(parser.db)))
                        return
        
        # coffeescript bug
        test_path = os.path.realpath(test_path)
        cmd_prefix = self.conf.node_cmd_prefix or []
        utils.run(cmd_prefix + ['coffee', '-c', '-o', self.conf.gen_path, test_path])
        extra_files = ['utils.coffee', 'search_index.coffee', 'watchdog.coffee']
        for file in extra_files:
            utils.run(cmd_prefix + ['coffee', '-c', '-o', self.conf.gen_path, os.path.join(os.path.dirname(test_path), file)])
        compiled_js_path = os.path.join(self.conf.gen_path, os.path.basename(test_path).replace('.coffee', '.js'))
        if not os.path.exists(compiled_js_path):
            raise CoffeeFailError('Coffee file was not compiled: %s -> %s' % (test_path, compiled_js_path))
        watchdog_js_path = os.path.join(self.conf.gen_path, 'watchdog.js')
        # prepend watchdog to the test, as watchdog alone does not work
        # as intended (casper/phantom wait for the timeout to occur)
        with open(watchdog_js_path) as f:
            text = f.read()
        with open(compiled_js_path) as f:
            text += f.read()
        with open(compiled_js_path, 'w') as f:
            f.write(text)
        
        utils.casper(self.conf, compiled_js_path, pre=self.casper_config_path)
    
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
        utils.clone_repo(self.conf.baseline_src,
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
        output_dir = self.conf.gen_path
        utils.mkdir_p(output_dir)
        output_path = os.path.join(output_dir, config_file_name.replace('.yaml', '.js'))
        with open(output_path, 'wb') as f:
            f.write(json)
        return output_path
    
    # mysql only
    def switch_posts_to_myisam(self):
        with self.db.cursor() as c:
            c.execute('alter table phpbb_posts engine=myisam')
