import subprocess
import sys
import os
from package.utils import Utils
from package.sqlparse import SQLParse

if sys.executable and "python" in sys.executable.lower():
    import sqlite3
    jython = False

else:
    from java.sql import DriverManager
    jython = True


class Database:
    def __init__(self, database, pragma = True):
        self.database = database
        if jython:
            self.dbConn = DriverManager.getConnection("jdbc:sqlite:{}".format(self.database))
        else:
            self.dbConn = sqlite3.connect(self.database)

        if pragma:
            self.execute_pragma()
    
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
        self.execute_query("PRAGMA journal_mode = DELETE")
        self.execute_query("PRAGMA wal_checkpoint(FULL)")
        
    
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

    @staticmethod
    def get_drp_output(databases, report_path):
        listing = {}
        for database in databases:
            path = os.path.normpath(database.replace(report_path, ""))
            content = SQLParse.read_contents(database)
            if content:
                listing[path] = content
        return listing

    #not necessary, remove in future?
    '''
    @staticmethod
    def export_columns_from_database(folder_path):
        meaning = Meaning()
        path = os.path.join(folder_path, 'DumpColumns.csv')
        print("[Utils] Dumping Columns to CSV. Base path {}".format(path))
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['database', 'table', 'column', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
            for db in Utils.list_files(folder_path, filter_type = [".db"]):
                database_name = db.split("/")[-1]
                for table, columns in DatabaseParser.dump_columns(database = db).items():
                    meanings = meaning.get_meaning(database_name, table)
                    item = {}
                    item["database"] = db.replace(folder_path, '') #remove basepath
                    item["table"] = table
                    
                    for column in columns:
                        item["column"] = column
                        if meanings:
                            item["description"] = meanings.get(column)

                        writer.writerow(item)

    '''
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
    