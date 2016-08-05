import urllib
from time import mktime
from datetime import datetime
from pprint import pprint as pp
import click

import feedparser
from tvoverlord.tvutil import sxxexx, hash2magnet
from tvoverlord.util import U


class Provider():
    name = 'Bit Torrent Scene'
    provider_urls = ['http://www.btstorr.cc/']
    shortname = 'BT'

    def search(self, search_string, season=False, episode=False):

        if season and episode:
            search_string = '%s %s' % (search_string, sxxexx(season, episode))

        query = urllib.parse.quote(search_string)

        show_data = []
        for try_url in self.provider_urls:
            url = '%s/rss/type/search/x/%s/' % (try_url, query)
            self.url = url
            parsed = feedparser.parse(url)

            if len(parsed['entries']) == 0:
                continue

            for show in parsed['entries']:
                if not show:
                    continue
                if show['published_parsed']:
                    dt = datetime.fromtimestamp(
                        mktime(show['published_parsed']))
                    date = dt.strftime('%b %d/%Y')
                else:
                    date = '-'

                size = show['size']
                title = show['title']
                seeds = show['seeds']
                magnet = hash2magnet(show['hash'], title)

                show_data.append([
                    title,
                    size,
                    date,
                    seeds,
                    self.shortname,
                    magnet
                ])

            # return without trying any more urls, this one has data.
            return show_data

        # return the empty show_data empty array
        return show_data

if __name__ == '__main__':
    from tvoverlord.consoletable import ConsoleTable
    # some simple tests
    p = Provider()
    data = p.search('game of thrones', season=6, episode=6)
    results = [
        [
            "wazup?",
            ['A', 'b', 'c', 'd'],
            [0, 10, 12, 10],
            ['<', '<', '<', '<'],
        ],
        data
    ]
    pp(results)
    click.echo(len(results))

    c = ConsoleTable(results)
    c.generate()
