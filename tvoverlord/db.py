from tvoverlord.config import Config
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
        conn = sqlite3.connect(Config.db_file)
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

    def save_dest(self, hash, destination):
        sql = '''UPDATE tracking SET destination = :destination
                 WHERE lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash, 'destination': destination}
        self.run_sql(sql, values)

    def set_torrent_complete(self, hash):
        sql = '''UPDATE tracking SET complete = 1
                 WHERE lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash}
        self.run_sql(sql, values)

    def show_exists(self, id):
        sql = '''SELECT thetvdb_series_id, status FROM shows
                 WHERE thetvdb_series_id=:thetvdb_id'''
        values = {'thetvdb_id': id}
        data = self.run_sql(sql, values)

        if data:
            return True
        else:
            return False

    def get_downloaded_days(self, days=0):
        sql = '''SELECT download_date, show_title, filename, chosen_hash, season,
                   episode, chosen, one_off, complete, chosen, destination FROM tracking
                 WHERE julianday(date(download_date))
                       > (julianday(date('now'))-:days)'''
        values = {'days': days}
        data = self.run_sql(sql, values)
        return data

    def get_downloaded_date(self, date):
        sql = '''SELECT download_date, show_title, filename, chosen_hash, season,
                   episode, chosen, one_off, complete, chosen, destination FROM tracking
                 WHERE date(download_date) = :date'''
        date_str = date.strftime('%Y-%m-%d')
        values = {'date': date_str}
        data = self.run_sql(sql, values)
        return data

    def get_downloaded_title(self, title):
        sql = '''SELECT download_date, show_title, filename, chosen_hash, season,
                   episode, chosen, one_off, complete, chosen, destination FROM tracking
                 WHERE show_title like :title'''
        values = {'title': "%{}%".format(title)}
        data = self.run_sql(sql, values)
        return data

    def get_missing(self):
        sql = '''SELECT download_date, show_title, filename, chosen_hash, season,
                   episode, chosen, one_off, complete, chosen, destination FROM tracking
                 WHERE complete IS NULL'''
        data = self.run_sql(sql)
        return data
