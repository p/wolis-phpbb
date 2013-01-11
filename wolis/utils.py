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
            actual_version = current.phpbb_version or PhpbbVersion(self.config)
            if not actual_version.matches(spec):
                print('Skipping test due to phpBB version constraint (%s)' % spec)
            else:
                return fn(self, *args, **kwargs)
        
        return decorated
    
    return decorator
