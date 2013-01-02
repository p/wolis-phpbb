import subprocess

def sudo(cmd):
    run = ['sudo', '-u', 'php']
    run.extend(cmd)
    subprocess.check_call(run)

def sudo_chmod(path, mode):
    sudo(['chmod', oct(mode), str(path)])
