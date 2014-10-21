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
    import dateutil.parser
    import json
    from pprint import pprint as pp

    all_show_data = []

    t = Tracking()
    rows = t.display()
    print '%s downloaded' % len(rows)
    for i in rows:
        show_data = {}
        date = i[0]                               # date
        d = dateutil.parser.parse(date)
        d = d.strftime("%Y-%m-%d")
        show_data['date'] = d
        show_data['show_name'] = i[1]             # show name
        if i[2] and i[3]:                         # season and episode
            show_data['episode_number'] = 'S%sE%s' % (i[2].rjust(2, '0'), i[3].rjust(2, '0'))
        else:
            show_data['episode_number'] = '(non db show)'

        data = json.loads(i[4])
        torrent_count = 0
        for torrent in data[1]:
            torrent_count += int(torrent[3])
        show_data['torrent_count'] = torrent_count
        all_show_data.append(show_data)

    sorted_data = sorted(all_show_data, key=lambda k: k['torrent_count'])
    for i in sorted_data:
        print i['show_name'].ljust(20),
        print i['episode_number'],
        print i['date'],
        print '-', i['torrent_count']
