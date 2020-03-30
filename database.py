try:
    import sqlite3
except:
    from jythonsqlite3 import module as sqlite3

import subprocess

class DatabaseParser:
    #https://svn.python.org/projects/python/trunk/Lib/sqlite3/dump.py
    @staticmethod
    def dump_columns(database):
        tables = {}
        #print("Reading {}".format(database))
        connection = sqlite3.connect(database)
        cu = connection.cursor()

        #Tables
        q = """SELECT name, type, sql FROM sqlite_master WHERE sql NOT NULL AND type == 'table'"""
        schema_res = cu.execute(q)
        for table_name, type, sql in schema_res.fetchall():
            tables[table_name] = []
            if table_name.startswith('sqlite_'):
                continue

            res = cu.execute("PRAGMA table_info('%s')" % table_name)
            column_names = [str(table_info[1]) for table_info in res.fetchall()]
            for col in column_names:
                tables[table_name].append(col)
        
        #'index', 'trigger', or 'view'
        '''
        q = """SELECT name, type, sql FROM sqlite_master WHERE sql NOT NULL AND type IN ('index', 'trigger', 'view')"""
        schema_res = cu.execute(q)
        for name, type, sql in schema_res.fetchall():
            print('%s;' % sql)
            #pass
        '''
        
        return tables

    