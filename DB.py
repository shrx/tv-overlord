from tv_config import Config
import sqlite3


def dict_factory(cursor, row):
    """Changes the data returned from the db from a
    tupple to a dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class SqlLiteDB(object):
    def named_sql(self, sql, values=False):
        pass

    def run_sql(self, sql, values=False, named_fields=False):
        conn = sqlite3.connect(Config.user_db)
        if named_fields:
            conn.row_factory = dict_factory
        curs = conn.cursor()
        if values:
            results = curs.execute(sql, values)
        else:
            results = curs.execute(sql)
        rowsdata = []

        if results:
            for i in results:
                rowsdata.append(i)

        conn.commit()
        conn.close()
        return rowsdata
