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

MysqliDb = MysqlDb

class PostgresDb(Db):
    def drop_database(self, name):
        quoted_name = pipes.quote(name)
        # --if-exists is missing on postgres 8.4
        # XXX hack for now
        #subprocess.check_call('dropdb -U pgsql --if-exists %s' % quoted_name, shell=True)
        subprocess.call('dropdb -U pgsql %s' % quoted_name, shell=True)
    
    def create_database(self, name):
        quoted_name = pipes.quote(name)
        subprocess.check_call('createdb -U pgsql -O wolis %s' % quoted_name, shell=True)
