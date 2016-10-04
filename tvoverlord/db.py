from tvoverlord.config import Config
from pprint import pprint as pp
import sqlite3
import json


def dict_factory(cursor, row):
    """Changes the data returned from the db from a
    tupple to a dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database(object):
    def configure(self):
        self.conn = sqlite3.connect(Config.db_file)

    def named_sql(self, sql, values=False):
        pass

    def run_sql(self, sql, values=False, named_fields=False):
        if named_fields:
            self.conn.row_factory = dict_factory
        curs = self.conn.cursor()
        if values:
            results = curs.execute(sql, values)
        else:
            results = curs.execute(sql)
        rowsdata = []

        if results:
            for i in results:
                rowsdata.append(i)

        self.conn.commit()
        return rowsdata

    def get_show_count(self):
        sql = '''SELECT COUNT(*) FROM shows'''
        data = self.run_sql(sql)[0][0]
        return data

    def get_show_info(self, hash):
        sql = '''SELECT  show_title, tracking.season,
                         tracking.episode,  search_engine_name
                 FROM tracking
                 INNER JOIN shows
                   ON tracking.show_title = shows.name
                 WHERE  lower(chosen_hash) = lower(:hash)'''
        values = {'hash': hash}

        data = self.run_sql(sql, values, named_fields=True)[0]
        return data['show_title'], data['search_engine_name'], data['season'], data['episode']

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

    def set_config(self, key, value):
        """Insert or update a key, value in the settings table

        This depends on the table settings having a table constraint
        of `UNIQUE(key)`

        CREATE TABLE settings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          key TEXT,
          value TEXT,
          UNIQUE(key)
        )
        """

        sql = """
            INSERT OR REPLACE INTO settings (key, value)
            values ('%s', :value)
        """ % key
        value = json.dumps(value)
        values = {'value': value}
        self.run_sql(sql, values)

    def get_config(self, key):
        sql = """
            SELECT * FROM settings
            WHERE key = :key
        """
        values = {'key': key}
        result = self.run_sql(sql, values)

        try:
            value = result[0][2]
            value = json.loads(value)
        # no JSONDecodeError in python 3.4
        # its a ValueError instead
        # except json.decoder.JSONDecodeError:
            # value = False
        except ValueError:
            value = False
        except IndexError:
            value = False

        return value

DB = Database()
