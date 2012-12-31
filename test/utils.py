import subprocess

def sudo_chmod(path, mode):
    subprocess.check_call(['sudo', '-u', 'php', 'chmod', oct(mode), str(path)])
