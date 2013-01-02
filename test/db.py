import pipes
import subprocess

class Db(object):
    def drop_database(self, name):
        raise NotImplementedError
    
    def create_database(self, name):
        raise NotImplementedError

class MysqlDb(Db):
    def drop_database(self, name):
        quoted_name = pipes.quote(name)
        subprocess.check_call('echo drop database if exists %s |mysql -u root' % quoted_name, shell=True)
    
    def create_database(self, name):
        quoted_name = pipes.quote(name)
        subprocess.check_call('echo create database %s |mysql -u root' % quoted_name, shell=True)
