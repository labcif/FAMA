import sys
import os
from package.utils import Utils


if sys.executable and "python" in sys.executable.lower():
    import sqlite3
    jython = False

else:
    from java.sql import DriverManager
    jython = True

import subprocess

class Database:
    def __init__(self, database):
        self.database = database
        if jython:
            self.dbConn = DriverManager.getConnection("jdbc:sqlite:{}".format(self.database))
        else:
            self.dbConn = sqlite3.connect(self.database)

    
    def execute_query(self, query, attach = None):
        if jython:
            contents = []
            stmt = self.dbConn.createStatement()
            if attach:
                stmt.execute(attach)

            result = stmt.executeQuery(query)
            while result.next():
                row = []
                for index in range(result.getMetaData().getColumnCount()):
                    #row[result.getMetaData().getColumnName(index + 1)] = result.getObject(index + 1) #to se as dict instead
                    row.append(result.getObject(index + 1))
                
                contents.append(row)
            
            return contents
        else:
            cursor_msg = self.dbConn.cursor()
            if attach:
                cursor_msg.execute(attach)

            cursor_msg.execute(query)
            return cursor_msg.fetchall()
    

    def execute_pragma(self):
        query = "PRAGMA table_info('%s')" % self.database

        if jython:
            stmt = self.dbConn.createStatement()
            stmt.executeQuery(query)
        else:
            cu = self.dbConn.cursor()
            cu.execute(query)
    
    @staticmethod
    def get_undark_output(databases, report_path):
        output = {}

        for name in databases:
            listing = []
            undark_output = Utils.run_undark(name).decode()
            for line in undark_output.splitlines():
                listing.append(line)
            
            if listing:
                relative_name = os.path.normpath(name.replace(report_path, "")) #clean complete path
                output[relative_name] = listing
        return output



### OLD CODE, MAYBE USEFUL IN FUTURE???
'''
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
        #q = """SELECT name, type, sql FROM sqlite_master WHERE sql NOT NULL AND type IN ('index', 'trigger', 'view')"""
        #schema_res = cu.execute(q)
        #for name, type, sql in schema_res.fetchall():
        #    print('%s;' % sql)
        #    #pass
        
        return tables
'''
    