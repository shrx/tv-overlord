import sqlite3

from tvoverlord.series import Series
from tvoverlord.config import Config
from tvoverlord.tvutil import dict_factory


class AllSeries:
    """
    Return an iterable class of Series

    Methods
    -------
    nameFilter(name)
      A string that used in the sql query to
      select LIKE matches on the show "name" field
    sort_by_date()
      Sort the results by date instead of the
      default 'name'
    """

    def __init__(self):
        self.sqlfilter = ''
        self.sort_field = "replace (name, 'The ', '')"

    def __iter__(self):
        self.dbdata = self._query_db(self.sqlfilter)
        self.index = len(self.dbdata)
        self.i = 0
        return self

    def __next__(self):
        if self.i == len(self.dbdata):
            raise StopIteration
        series = Series(dbdata=self.dbdata[self.i])
        self.i += 1
        return series

    def name_filter(self, name):
        show_name = 'name LIKE "%%%s%%"' % name
        self.sqlfilter = show_name

    def sort_by_date(self):
        self.sort_field = 'next_episode, name'

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
                %s;""" % (
            sqlfilter,
            self.sort_field
        )
        conn = sqlite3.connect(Config.db_file)
        # conn.row_factory = tv_util.dict_factory
        conn.row_factory = dict_factory
        curs = conn.cursor()
        ddata = curs.execute(sql)
        data = []
        for i in ddata:
            data.append(i)
        conn.commit()
        conn.close()
        return data
