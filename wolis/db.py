import pipes
import subprocess

class Db(object):
    def __init__(self, conf):
        self.conf = conf
    
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
        import psycopg2
        import contextlib
        
        conn = psycopg2.connect(database='postgres', user=self.conf.get('user'), password=self.conf.get('password'))
        # http://stackoverflow.com/questions/1017463/postgresql-how-to-run-vacuum-from-code-outside-transaction-block
        conn.set_isolation_level(0)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('drop database if exists %s' % name)
        conn.close()
    
    def create_database(self, name):
        import psycopg2
        import contextlib
        
        conn = psycopg2.connect(database='postgres', user=self.conf.get('user'), password=self.conf.get('password'))
        # http://stackoverflow.com/questions/1017463/postgresql-how-to-run-vacuum-from-code-outside-transaction-block
        conn.set_isolation_level(0)
        with contextlib.closing(conn.cursor()) as c:
            c.execute('create database %s' % name)
        conn.close()
