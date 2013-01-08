import os.path
import subprocess

def sudo(user, cmd, **kwargs):
    run = ['sudo', '-u', user]
    run.extend(cmd)
    subprocess.check_call(run, **kwargs)

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
    sudo_rvm(['casperjs', path])

def git_in_dir(dir, *args):
    cmd = ['git',
        '--git-dir', os.path.join(dir, '.git'),
        '--work-tree', dir]
    cmd.extend(args)
    subprocess.check_call(cmd)
