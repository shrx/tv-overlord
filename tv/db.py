from tv.tvconfig import Config
from pprint import pprint as pp
import sqlite3


def dict_factory(cursor, row):
    """Changes the data returned from the db from a
    tupple to a dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DB(object):
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

    def get_show_info(self, hash):
        sql = '''SELECT show_title, season, episode
                 FROM tracking
                 WHERE lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash}

        data = self.run_sql(sql, values, named_fields=True)[0]
        return data['show_title'], data['season'], data['episode']

    def is_oneoff(self, hash):
        sql = '''SELECT one_off FROM tracking
                 WHERE lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash}

        data = self.run_sql(sql, values, named_fields=True)[0]
        return data['one_off']

    def save_info(self, hash, filename):
        sql = '''UPDATE tracking SET filename = :filename
                 WHERE lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash, 'filename': filename}
        self.run_sql(sql, values)

    def set_torrent_complete(self, hash):
        sql = '''UPDATE tracking SET complete = 1
                 WHERE lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash}
        data = self.run_sql(sql, values)

