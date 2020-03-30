from java.lang import String
from java.util import Properties
from org.sqlite import SQLiteConnection

def connect(url):
    return Connection("", url)


class Connection(SQLiteConnection):

    def cursor(self):
        return Cursor(self)

    def execute(self, sql):
        return self.cursor().execute(sql)


class Cursor:

    def __init__(self, connection):
        self._conn   = connection
        self._result = None
        self._rmeta  = None
        self._status = None
        self._stmt   = None

    def execute(self, sql):
        self._result = None
        self._rmeta  = None
        self._stmt   = self._conn.createStatement()
        self._status = self._stmt.execute(sql)
        count = self._stmt.getUpdateCount()
        if count == -1:
            self._result = self._stmt.getResultSet()
            self._rmeta  = self._result.getMetaData()
        else:
            self._result = count

    def fetchone(self):
        return self._fetch("one")

    def fetchmany(self, n):
        return self._fetch("many", n)

    def fetchall(self):
        return self._fetch("all")

    def _fetch(self, size, n = 0):
        if self._result is None or self._result.next() == False:
            raise Error("resultset is empty")
        if size == "one":
            value = self._get_row()
        elif size == "many":
            value = [self._get_row()]
            for i in range(n):
                if self._result.next():
                    value.append(self._get_row())
                else:
                    break
        else:
            value = [self._get_row()]
            while self._result.next():
                value.append(self._get_row())
        return value

    def _get_row(self):
        row = list()
        n_columns = self._rmeta.getColumnCount()
        for i in range(1, (n_columns + 1)):
            row.append(self._result.getObject(i))
        return tuple(row)
