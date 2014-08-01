import sqlite3
import json
import datetime
from tv_config import Config


class Tracking(object):

    def __init__(self):
        config = Config()

        sql = '''
            CREATE TABLE IF NOT EXISTS tracking (
                date TEXT,
                show_title TEXT,
                season TEXT,
                episode TEXT,
                data TEXT,
                chosen TEXT
            );'''
        self.run_sql(sql)

    def save(self, show_title, season, episode, data, chosen):
        data = json.dumps(data)
        now = datetime.datetime.today()
        date = now.isoformat()
        sql = '''
            INSERT INTO tracking(
                date, show_title, season, episode, data, chosen)
            VALUES(
                :date, :show_title, :season, :episode, :data, :chosen);'''

        values = {
            'date': date,
            'show_title' : show_title,
            'season': season,
            'episode': episode,
            'data': data,
            'chosen': chosen,
        }

        self.run_sql(sql, values)

    def display(self):
        sql = '''
            SELECT * FROM tracking;
        '''
        rows = self.run_sql(sql)
        return rows

    def run_sql(self, sql, values=False):
        conn = sqlite3.connect(Config.user_db)
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

if __name__ == '__main__':
    t = Tracking()
    rows = t.display()
    print 'length:', len(rows)
    for i in rows:
        dt = datetime.datetime
        print i[0], '-', i[1], 'S%sE%s' % (i[2].rjust(2, '0'), i[3].rjust(2, '0'))
