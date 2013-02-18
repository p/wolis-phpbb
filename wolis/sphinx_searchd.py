import socket
import os
import subprocess
from . import utils

def copy_cmd(cmd):
    if cmd:
        cmd = list(cmd)
    else:
        cmd = []
    return cmd

class SearchdManager(object):
    def __init__(self, conf):
        self.conf = conf
    
    def start(self):
        # kill previous instances
        cmd = copy_cmd(self.conf.sphinx_cmd_prefix)
        cmd += ['pkill', 'searchd']
        try:
            utils.run(cmd)
        except:
            pass
        
        cmd = copy_cmd(self.conf.sphinx_cmd_prefix)
        cmd += ['searchd', '-c', self.conf.sphinx_config_path]
        utils.run(cmd)
        
        # fix permissions on pid file (0600 for some reason initially)
        cmd = copy_cmd(self.conf.sphinx_cmd_prefix)
        cmd += ['chmod', '0644', self.conf.sphinx_pidfile_path]
        utils.run(cmd)
    
    def stop(self):
        if self.pid():
            self.kill_sphinx()
    
    def ensure_running(self):
        if not self.is_running():
            self.start()
            self.wait_to_start()
            assert self.pid_alive()
    
    def ensure_stopped(self):
        if self.is_running():
            self.stop()
            self.wait_to_stop()
            assert not self.pid_alive()
        utils.run((self.conf.sphinx_cmd_prefix or []) + ['pkill', 'searchd'])
    
    def pid(self):
        try:
            with open(self.conf.sphinx_pidfile_path) as f:
                pid = int(f.read().strip())
        except IOError:
            # file not found, etc.
            pid = None
        except ValueError:
            # pid file empty
            pid = None
        return pid
    
    def pid_alive(self):
        #pid = self.pid()
        try:
            self.kill_sphinx(0)
            alive = True
        except (OSError, subprocess.CalledProcessError):
            # missing process or no permissions
            alive = False
        return alive
    
    def kill_sphinx(self, signal):
        pid = self.pid()
        assert pid
        if self.conf.sphinx_cmd_prefix:
            cmd = copy_cmd(self.conf.sphinx_cmd_prefix)
            cmd += ['kill', '-%d' % signal, str(pid)]
            utils.run(cmd)
        else:
            os.kill(pid, signal)
    
    def is_running(self):
        if not self.pid() or not self.pid_alive():
            return False
        try:
            conn = socket.create_connection(('127.0.0.1', self.conf.sphinx_searchd_port), 0.1)
        except socket.error as e:
            running = False
        else:
            conn.close()
            running = True
        return running
    
    def wait_to_stop(self):
        ok = False
        for i in range(10):
            try:
                conn = socket.create_connection(('127.0.0.1', self.conf.sphinx_searchd_port), 0.1)
            except socket.error as e:
                ok = True
                break
            else:
                conn.close()
                _time.sleep(0.1)
        if not ok:
            raise SearchdError('searchd did not stop listening after 1 second')
    
    def wait_to_start(self):
        ok = False
        for i in range(10):
            try:
                conn = socket.create_connection(('127.0.0.1', self.conf.sphinx_searchd_port), 0.1)
            except socket.error as e:
                _time.sleep(0.1)
            else:
                conn.close()
                ok = True
                break
        if not ok:
            raise SearchdError('searchd did not start listening after 1 second')
