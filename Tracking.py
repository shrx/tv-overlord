import json
import datetime
from DB import SqlLiteDB


class Tracking(SqlLiteDB):
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


if __name__ == '__main__':
    import dateutil.parser

    t = Tracking()
    rows = t.display()
    print '%s downloaded' % len(rows)
    for i in rows:
        date = i[0]          # date
        d = dateutil.parser.parse(date)
        d = d.strftime("%Y-%m-%d")
        print d, '-',
        print i[1],          # show name
        if i[2] and i[3]:    # season and episode
            print 'S%sE%s' % (i[2].rjust(2, '0'), i[3].rjust(2, '0'))
        else:
            print '(non db show)'
