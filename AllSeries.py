import sqlite3
from Series import Series
from tv_config import Config


class AllSeries:
    """
    Return an iterable class of Series

    Methods
    -------
    nameFilter(name)
      A string that used in the sql query to
      select LIKE matches on the show "name" field
    """

    def __init__(self, provider):
        self.provider = provider
        self.sqlfilter = ''

    def __iter__(self):
        self.dbdata = self._query_db(self.sqlfilter)
        self.index = len(self.dbdata)
        self.i = 0
        return self

    def next(self):
        if self.i == len(self.dbdata):
            raise StopIteration
        series = Series(self.provider, dbdata=self.dbdata[self.i])
        self.i += 1
        return series

    def name_filter(self, name):
        show_name = 'name LIKE "%%%s%%"' % name
        self.sqlfilter = show_name

    def _query_db(self, sqlfilter=''):
        if sqlfilter:
            sqlfilter = 'AND %s' % sqlfilter
        sql = """
            SELECT
                name,
                season,
                episode,
                thetvdb_series_id,
                ragetv_series_id,
                search_engine_name,
                status
            FROM
                shows
            WHERE
                status='active'
                %s
            ORDER BY
                replace (name, 'The ', '');""" % (
            sqlfilter,
        )
        conn = sqlite3.connect(Config.db_file)
        conn.row_factory = self.dict_factory
        curs = conn.cursor()
        ddata = curs.execute(sql)
        data = []
        for i in ddata:
            data.append(i)
        conn.commit()
        conn.close()
        return data

    @staticmethod
    def dict_factory(cursor, row):
        """Changes the data returned from the db from a
        tupple to a dictionary"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
