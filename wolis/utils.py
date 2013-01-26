import os.path
import re

class RunError(StandardError):
    pass

def run(cmd, **kwargs):
    import subprocess
    
    if 'stdout_io' in kwargs:
        # XXX unfinished
        stdout_io = kwargs['stdout_io']
        del kwargs['stdout_io']
        kwargs['stdout'] = subprocess.PIPE
        no_check = kwargs.get('no_check')
        p = Popen(cmd, **kwargs)
        out, err = p.communicate()
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
    
    return os.path.join(os.path.dirname(__file__), '../script', file)

# XXX do something about the config parameter
def casper(conf, path, pre=None):
    path = os.path.realpath(path)
    cmd_prefix = conf.node_cmd_prefix or []
    # workaround for https://github.com/n1k0/casperjs/issues/343 -
    # pass through coffeescript first
    #with open('/dev/null', 'wb') as f:
        #run(cmd_prefix + ['coffee', '-cp', path], stdout=f)
    casperjs_wrapper = our_script_path('casperjs-wrapper')
    cmd = [casperjs_wrapper, 'test', path]
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
        git_in_dir(dest, 'fetch', '-pt', remote_name)

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

class Current(object):
    phpbb_version = None
    config = None

current = Current()

def restrict_phpbb_version(spec):
    def decorator(fn):
        def decorated(self, *args, **kwargs):
            actual_version = current.phpbb_version or PhpbbVersion(self.conf)
            if not actual_version.matches(spec):
                print('Skipping %s due to phpBB version constraint (%s)' % (fn.__name__, spec))
            else:
                return fn(self, *args, **kwargs)
        
        return decorated
    
    return decorator
