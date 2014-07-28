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
                data TEXT,
                chosen TEXT
            );'''
        self.run_sql(sql)

    def save(self, data, chosen):

        data = json.dumps(data)
        now = datetime.datetime.today()
        date = now.isoformat()
        sql = '''
            INSERT INTO tracking(
                date, data, chosen)
            VALUES(
                :date, :data, :chosen);'''

        values = {
            'date': date,
            'data': data,
            'chosen': chosen,
        }

        self.run_sql(sql, values)

    def run_sql(self, sql, values=False):
        conn = sqlite3.connect(Config.user_db)
        curs = conn.cursor()
        if values:
            curs.execute(sql, values)
        else:
            curs.execute(sql)
        conn.commit()
        conn.close()


if __name__ == '__main__':
    pass
