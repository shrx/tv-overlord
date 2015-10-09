import json
import datetime
import urlparse
from DB import SqlLiteDB


class Tracking(SqlLiteDB):
    def __init__(self):

        sql = '''
            CREATE TABLE IF NOT EXISTS tracking (
                download_date TEXT,
                show_title TEXT,
                season TEXT,
                episode TEXT,
                download_data TEXT,
                chosen TEXT,
                chosen_hash TEXT
            );'''
        self.run_sql(sql)

    def save(self, show_title, season, episode, data, chosen_url):
        magnet_hash = self._extract_hash(chosen_url)
        data, chosen = self._remove_urls(data, chosen_url)
        data = json.dumps(data)
        now = datetime.datetime.today()
        date = now.isoformat()
        sql = '''
            INSERT INTO tracking(
                download_date, show_title, season, episode, download_data, chosen, chosen_hash)
            VALUES(
                :date, :show_title, :season, :episode, :data, :chosen, :hash);'''

        values = {
            'date': date,
            'show_title' : show_title,
            'season': season,
            'episode': episode,
            'data': data,
            'chosen': chosen,
            'hash': magnet_hash,
        }

        self.run_sql(sql, values)

    def _remove_urls(self, data, chosen):
        '''Remove the magnet url's from the data since they have no use
        for data analysis and they take up to much room in the db
        '''
        for i in range(len(data[1])):
            url = data[1][i][4]
            if url == chosen:
                chosen = i
            data[1][i][4] = i

        return data, chosen

    def _extract_hash(self, url):
        if not url.startswith('magnet:'):
            print 'Warning: url is not a magnet'
            print url
            return ''
        parsed_url = urlparse.urlparse(url)
        #print 'a', parsed_url
        magnet_hash = urlparse.parse_qs(parsed_url.query)['xt']
        #print 'b', magnet_hash
        if len(magnet_hash) > 1:
            print 'multple hashes:'
            print magnet_hash

        magnet_hash = magnet_hash[0].split(':')[-1]
        #print 'c', magnet_hash
        #exit()

        return magnet_hash

    def display(self):
        sql = '''
            SELECT * FROM tracking;
        '''
        rows = self.run_sql(sql, named_fields=True)
        return rows


if __name__ == '__main__':
    pass
