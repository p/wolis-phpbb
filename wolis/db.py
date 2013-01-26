import re
import contextlib

class Db(object):
    def __init__(self, conf):
        self.conf = conf
    
    def drop_database(self, name):
        raise NotImplementedError
    
    def create_database(self, name):
        raise NotImplementedError

class MysqlDb(Db):
    def drop_database(self, name):
        assert re.match(r'\w+$', name)
        with self._cursor() as c:
            c.execute('drop database if exists %s' % name)
    
    def create_database(self, name):
        assert re.match(r'\w+$', name)
        with self._cursor() as c:
            c.execute('create database %s' % name)
    
    def _connect(self):
        import MySQLdb
        
        kwargs = dict(host=self.conf.get('host'), user=self.conf.get('user'), passwd=self.conf.get('password'))
        # mysql... does not accept None in values
        for key in kwargs.keys():
            if kwargs[key] is None:
                del kwargs[key]
        conn = MySQLdb.connect(**kwargs)
        return conn
    
    @contextlib.contextmanager
    def _cursor(self):
        with contextlib.closing(self._connect()) as conn:
            with contextlib.closing(conn.cursor()) as c:
                yield c

MysqliDb = MysqlDb

class PostgresDb(Db):
    def drop_database(self, name):
        assert re.match(r'\w+$', name)
        with self._non_tx_cursor('postgres') as c:
            c.execute('drop database if exists %s' % name)
    
    def create_database(self, name):
        assert re.match(r'\w+$', name)
        with self._non_tx_cursor('postgres') as c:
            c.execute("create database %s encoding 'utf-8'" % name)
    
    def _connect(self, dbname):
        import psycopg2
        
        conn = psycopg2.connect(database=dbname, host=self.conf.get('host'), user=self.conf.get('user'), password=self.conf.get('password'))
        return conn
    
    @contextlib.contextmanager
    def _non_tx_cursor(self, dbname):
        with contextlib.closing(self._connect('postgres')) as conn:
            # http://stackoverflow.com/questions/1017463/postgresql-how-to-run-vacuum-from-code-outside-transaction-block
            conn.set_isolation_level(0)
            with contextlib.closing(conn.cursor()) as c:
                yield c
