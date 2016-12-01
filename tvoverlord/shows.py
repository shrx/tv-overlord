import sqlite3
import click

from tvoverlord.show import Show
from tvoverlord.config import Config
from tvoverlord.tvutil import dict_factory
from tvoverlord.db import DB


class Shows:
    """
    Return an iterable class of Shows

    Methods
    -------
    nameFilter(name)
      A string that used in the sql query to
      select LIKE matches on the show "name" field
    sort_by_date()
      Sort the results by date instead of the
      default 'name'
    """

    def __init__(self, name_filter='', by_date=False, status='active'):
        sqlfilter = ''
        if name_filter:
            sqlfilter = self.filter_by_name(name_filter)

        if by_date:
            self.sort_field = 'next_episode, name'
        else:
            self.sort_field = "replace (name, 'The ', '')"

        if status == 'active':
            statusfilter = 'status="active"'
        elif status == 'inactive':
            statusfilter = 'status="inactive"'
        elif status == 'all':
            statusfilter = 'status in ("active", "inactive")'
        elif not status:
            statusfilter = 'status="active"'

        self.dbdata = self._query_db(sqlfilter, statusfilter)
        self.show_count = len(self.dbdata)


    def __iter__(self):
        self.index = len(self.dbdata)
        self.i = 0
        return self

    def __next__(self):
        if self.i == len(self.dbdata):
            raise StopIteration
        show = Show(dbdata=self.dbdata[self.i])
        self.i += 1
        return show

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

    def _query_db(self, sqlfilter, statusfilter):
        # print('>>>',sqlfilter, '|', statusfilter)
        # if sqlfilter:
            # sqlfilter = 'AND %s' % sqlfilter

        # print('sqlfilter: %s, statusfilter: %s' % (sqlfilter, statusfilter))
        if statusfilter and sqlfilter:
            where = '%s AND %s' % (statusfilter, sqlfilter)
        elif sqlfilter:
            where = sqlfilter
        elif statusfilter:
            where = statusfilter

        sql = """
            SELECT
                name,
                season,
                episode,
                search_by_date,
                date_format,
                thetvdb_series_id,
                ragetv_series_id,
                search_engine_name,
                status
            FROM
                shows
            WHERE
                %s
            ORDER BY
                %s;""" % (
            where,
            self.sort_field
        )
        ddata = DB.run_sql(sql, named_fields=True)
        data = []
        for i in ddata:
            data.append(i)
        self.show_count = len(data)
        return data
