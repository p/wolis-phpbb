import os.path
import subprocess

def sudo(user, cmd, **kwargs):
    run = ['sudo', '-u', user]
    run.extend(cmd)
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
    fn(run, **kwargs)

def sudo_php(cmd):
    sudo('php', cmd)

def sudo_rvm(cmd, **kwargs):
    run = ['-iH']
    run.extend(cmd)
    sudo('rvm', run, **kwargs)

def sudo_chmod(path, mode):
    sudo_php(['chmod', oct(mode), str(path)])

def rsync(src, dest, delete=False, exclude=None):
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

def casper(path):
    path = os.path.realpath(path)
    # workaround for https://github.com/n1k0/casperjs/issues/343 -
    # pass through coffeescript first
    with open('/dev/null', 'wb') as f:
        sudo_rvm(['coffee', '-cp', path], stdout=f)
    casperjs_wrapper = os.path.join(os.path.dirname(__file__), '../script/casperjs-wrapper')
    sudo_rvm([casperjs_wrapper, 'test', path])

def git_in_dir(dir, *args):
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
