import json
import datetime
import urllib.parse
from pprint import pprint as pp
import click

from tvoverlord.db import DB


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
        data = json.dumps(data)
        now = datetime.datetime.today()
        date = now.isoformat()
        # oneoff is a show that was downloaded via 'nondbshow'
        oneoff = 0
        if not season or not episode:
            oneoff = 1

        sql = '''
            INSERT INTO tracking(
                download_date, show_title, season,
                episode, chosen, chosen_hash, one_off)
            VALUES(
                :date, :show_title, :season, :episode,
                :chosen, :hash, :one_off);'''

        values = {
            'date': date,
            'show_title': show_title,
            'season': season,
            'episode': episode,
            'chosen': chosen_url,
            'hash': magnet_hash,
            'one_off': oneoff,
        }

        self.run_sql(sql, values)

    def _extract_hash(self, url):
        if not url.startswith('magnet:'):
            return ''
        parsed_url = urllib.parse.urlparse(url)
        magnet_hash = urllib.parse.parse_qs(parsed_url.query)['xt']
        if len(magnet_hash) > 1:
            click.echo('multple hashes:')
            click.echo(magnet_hash)

        magnet_hash = magnet_hash[0].split(':')[-1]

        return magnet_hash

    def display(self):
        sql = '''
            SELECT * FROM tracking;
        '''
        rows = self.run_sql(sql, named_fields=True)
        return rows


if __name__ == '__main__':
    pass
