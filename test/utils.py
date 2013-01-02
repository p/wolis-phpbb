import os.path
import subprocess

def sudo(cmd):
    run = ['sudo', '-u', 'php']
    run.extend(cmd)
    subprocess.check_call(run)

def sudo_chmod(path, mode):
    sudo(['chmod', oct(mode), str(path)])

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

def git_in_dir(dir, *args):
    cmd = ['git',
        '--git-dir', os.path.join(dir, '.git'),
        '--work-tree', dir]
    cmd.extend(args)
    subprocess.check_call(cmd)
