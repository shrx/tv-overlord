import json
import datetime
from DB import SqlLiteDB


class Tracking(SqlLiteDB):
    def __init__(self):

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
        data, chosen = self._remove_urls(data, chosen)
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

    def _remove_urls(self, data, chosen):
        '''Remove the magnet url's from the data since they have no use
        for data analysis and they take up to much room in the db
        '''
        from pprint import pprint as pp

        for i in range(len(data[1])):
            url = data[1][i][4]
            if url == chosen:
                chosen = i
            data[1][i][4] = i

        return data, chosen

    def display(self):
        sql = '''
            SELECT * FROM tracking;
        '''
        rows = self.run_sql(sql)
        return rows


if __name__ == '__main__':
    pass
