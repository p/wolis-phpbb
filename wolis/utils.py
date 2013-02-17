import os.path
import re
import sys
import functools

class RunError(StandardError):
    pass

def flush_streams():
    sys.stdout.flush()
    sys.stderr.flush()

def run(cmd, **kwargs):
    import subprocess
    
    flush_streams()
    
    if 'return_stdout' in kwargs:
        del kwargs['return_stdout']
        kwargs['stdout'] = subprocess.PIPE
        no_check = kwargs.get('no_check')
        if no_check:
            del kwargs['no_check']
        p = subprocess.Popen(cmd, **kwargs)
        out, err = p.communicate()
        if not no_check:
            if p.returncode != 0:
                raise subprocess.CalledProcessError('Process finished with code %d' % p.returncode)
        return out
    
    if 'no_check' in kwargs:
        fn = subprocess.call
        del kwargs['no_check']
    else:
        fn = subprocess.check_call
    try:
        fn(cmd, **kwargs)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RunError, str(exc) + "\nCommand: %s" % repr(cmd)

def run_in_dir(dir, cmd, **kwargs):
    import os
    
    # for the benefit of fork-less platforms
    cwd = os.getcwd()
    os.chdir(dir)
    try:
        return run(cmd, **kwargs)
    finally:
        os.chdir(cwd)

def rsync(src, dest, delete=False, exclude=None):
    import subprocess
    
    cmd = ['rsync', '-a', '--exclude', '.git']
    if delete:
        cmd.append('--delete')
    if exclude:
        if isinstance(exclude, basestring):
            cmd.extend(['--exclude', exclude])
        else:
            for path in exclucde:
                cmd.extend(['--exclude', path])
    cmd.extend([src, dest])
    subprocess.check_call(cmd)

def our_script_path(file):
    '''Returns an absolute path to the specified file in our script
    directory.
    '''
    
    return os.path.realpath(os.path.join(os.path.dirname(__file__), '../script', file))

# XXX do something about the config parameter
def casper(conf, *paths, **kwargs):
    pre = kwargs.get('pre')
    #path = os.path.realpath(path)
    cmd_prefix = conf.node_cmd_prefix or []
    # workaround for https://github.com/n1k0/casperjs/issues/343 -
    # pass through coffeescript first
    #with open('/dev/null', 'wb') as f:
        #run(cmd_prefix + ['coffee', '-cp', path], stdout=f)
    casperjs_wrapper = our_script_path('casperjs-wrapper')
    cmd = [casperjs_wrapper, 'test'] + list(paths)
    if pre is not None:
        cmd.append('--pre=%s' % pre)
    run(cmd_prefix + cmd)

def git_in_dir(dir, *args):
    import subprocess
    
    cmd = ['git',
        '--git-dir', os.path.join(dir, '.git'),
        '--work-tree', dir]
    cmd.extend(args)
    subprocess.check_call(cmd)

def clone_repo(src, dest, remote_name):
    import subprocess
    
    if not os.path.exists(dest):
        try:
            subprocess.check_call(['git', 'init', dest])
            git_in_dir(dest, 'remote', 'add', remote_name, src, '-f')
        except:
            silent_rm_rf(dest)
            raise
    else:
        git_in_dir(dest, 'remote', 'set-url', remote_name, src)
        git_in_dir(dest, 'fetch', remote_name)
        git_in_dir(dest, 'fetch', '-t', remote_name)

def silent_rm_rf(path):
    if os.path.exists(path):
        import shutil
        try:
            shutil.rmtree(path)
        except:
            pass

def yaml_to_json(input_text=None, input_file=None, output_file=None):
    import yaml
    import json
    
    if input_text is not None:
        data = yaml.load(input_text)
    elif input_file is not None:
        if isinstance(input_file, basestring):
            with open(input_file, 'rb') as f:
                data = yaml.load(f)
        else:
            data = yaml.load(input_file)
    else:
        raise ArgumentError('Neither input_text nor input_file given')
    
    if output_file is not None:
        if isinstance(output_file, basestring):
            with open(output_file, 'wb') as f:
                json.dump(data, f)
        else:
            json.dump(data, output_file)
    else:
        return json.dumps(data)

def naive_strip_html(text):
    # http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
    return re.sub('<[^<]+?>', '', text)

def text_content(xml_node):
    import lxml.etree
    from . import html2text as _html2text
    
    xml = lxml.etree.tostring(xml_node)
    text = _html2text.html2text(xml)
    return text

# http://stackoverflow.com/questions/1111056/get-tz-information-of-the-system-in-python
def local_time_offset(t=None):
    """Return offset of local zone from GMT, either at present or at time t."""
    
    import time as _time
    
    # python2.3 localtime() can't take None
    if t is None:
        t = _time.time()

    if _time.localtime(t).tm_isdst and _time.daylight:
        return -_time.altzone
    else:
        return -_time.timezone

class PhpbbVersion(object):
    def __init__(self, conf):
        if os.path.exists(os.path.join(conf.test_root_phpbb, 'includes/extension/manager.php')):
            self.version = (3, 1, 0)
        else:
            self.version = (3, 0, 0)
    
    def __cmp__(self, other):
        return cmp(self.version, tuple(other))
    
    def __str__(self):
        return 'phpBB version %d.%d.%d' % self.version
    
    def matches(self, spec):
        if spec.startswith('>='):
            target_version = map(int, spec[2:].split('.'))
            return self >= target_version
        elif spec.startswith('<'):
            target_version = map(int, spec[1:].split('.'))
            return self < target_version
        else:
            raise NotImplementedError("Unsupported version specification: %s" % spec)
    
    def js(self):
        js = 'global.wolis.phpbb_version = [%d, %d, %d];' % self.version
        return js

class Current(object):
    phpbb_version = None
    config = None
    dbms = None
    db = None
    
    validation_errors = []

current = Current()

def restrict_phpbb_version(spec):
    def decorator(fn):
        @functools.wraps(fn)
        def decorated(self, *args, **kwargs):
            actual_version = current.phpbb_version or PhpbbVersion(self.conf)
            if not actual_version.matches(spec):
                print('Skipping %s due to phpBB version constraint (%s)' % (fn.__name__, spec))
            else:
                return fn(self, *args, **kwargs)
        
        return decorated
    
    return decorator

def db_matches(actual, requested):
    if requested == 'mysql*':
        return db_matches_list(actual, ['mysql', 'mysqli'])
    else:
        return actual == requested

def db_matches_list(actual, requested_list):
    if 'mysql*' in requested_list:
        requested_list = list(requested_list)
        requested_list.remove('mysql*')
        requested_list.append('mysql')
        requested_list.append('mysqli')
    return actual in requested_list

def restrict_database(*specs):
    def decorator(fn):
        @functools.wraps(fn)
        def decorated(self, *args, **kwargs):
            actual_dbms = current.dbms or self.conf.db
            if not db_matches_list(actual_dbms, specs):
                spec = '|'.join(specs)
                print('Skipping %s due to database requirement (%s)' % (fn.__name__, spec))
            else:
                return fn(self, *args, **kwargs)
        
        return decorated
    
    return decorator

def instantiate_db(conf, requested_dbms=None):
    from . import db
    
    driver = requested_dbms or conf.db.driver
    class_name = driver[0].upper() + driver[1:] + 'Db'
    cls = getattr(db, class_name)
    db = cls(getattr(conf, driver))
    return db

def retry_condition_fn(response):
    # 502 is sent when the backend php process sigsegvs
    # 200 with empty body is sent probably immediately afterwards
    return response.code == 502 or response.code == 200 and len(response.raw_body) == 0

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)
