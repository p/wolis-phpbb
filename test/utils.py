import subprocess

def sudo(cmd):
    run = ['sudo', '-u', 'php']
    run.extend(cmd)
    subprocess.check_call(run)

def sudo_chmod(path, mode):
    sudo(['chmod', oct(mode), str(path)])

def rsync(src, dest, delete=False):
    cmd = ['rsync', '-a', '--exclude', '.git']
    if delete:
        cmd.append('--delete')
    cmd.extend([src, dest])
    subprocess.check_call(cmd)
