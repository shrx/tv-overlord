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

    def __init__(self, name_filter='', by_date=False):
        sqlfilter = ''
        if name_filter:
            sqlfilter = self.filter_by_name(name_filter)

        if by_date:
            self.sort_field = 'next_episode, name'
        else:
            self.sort_field = "replace (name, 'The ', '')"
        self.dbdata = self._query_db(sqlfilter)
        self.show_count = len(self.dbdata)

    def __iter__(self):
        self.index = len(self.dbdata)
        self.i = 0
        return self

    def __next__(self):
        if self.i == len(self.dbdata):
            raise StopIteration
        series = Series(dbdata=self.dbdata[self.i])
        self.i += 1
        return series

    def __len__(self):
        return self.show_count

    def length(self):
        return self.show_count

    def filter_by_name(self, name):
        show_name = 'name LIKE "%%%s%%"' % name
        self.sqlfilter = show_name
        return show_name

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
        self.show_count = len(data)
        conn.commit()
        conn.close()
        return data
