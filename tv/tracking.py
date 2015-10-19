import json
import datetime
import urlparse

from tv.db import DB


class Tracking(DB):
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
        # Cleaned_data contains the data array without the magnet urls.
        # To use that, change cleaned_data to data
        cleaned_data, chosen = self._remove_urls(data, chosen_url)
        data = json.dumps(data)
        now = datetime.datetime.today()
        date = now.isoformat()
        # oneoff is a show that was downloaded via 'nondbshow'
        oneoff = 0
        if not season or not episode:
            oneoff = 1

        sql = '''
            INSERT INTO tracking(
                download_date, show_title, season, episode, download_data, chosen, chosen_hash, one_off)
            VALUES(
                :date, :show_title, :season, :episode, :data, :chosen, :hash, :one_off);'''

        values = {
            'date': date,
            'show_title' : show_title,
            'season': season,
            'episode': episode,
            'data': data,
            'chosen': chosen,
            'hash': magnet_hash,
            'one_off': oneoff,
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
