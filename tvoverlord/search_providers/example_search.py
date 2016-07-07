import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
from pprint import pprint as pp
import click

import feedparser


class Provider():
    # this is not used, but might be in the future
    name = 'Search engine name'

    # this is used for debugging.  It should be the full search url's used
    url = []

    # two letters, used for showing what search engine each episode is from
    shortname = 'SE'

    # the search method will be called once with the show name, season
    # and episode.  If the search is a nondbshow search, the season
    # and episode won't be set.  The data that gets returned is and
    # array of arrays.  Each nested array is a search result that has
    # the data in this order:
    # [title, size, date, seeds, shortname, magneturl]
    def search(self, search_string, season=False, episode=False):

        show_data = []

        show_data.append(['title', 'size', 'date', 'seeds',
                          self.shortname, 'magnet'])

        self.url = [
            'http://www.somesite.com/search/doctorwho'
        ]
        return show_data


if __name__ == '__main__':
    # some simple tests
    p = Provider()
    results = p.search('game of thrones', season=6, episode=6)
    click.echo(len(results))
