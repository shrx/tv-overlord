import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
from pprint import pprint as pp
import click

import feedparser


class Provider():
    # The name of the search engine.  This is used in `tvol config`
    name = 'Search engine name'

    # A list of all the urls searched.  If there is only one, it still
    # needs to be an array.  This is used in `tvol config`
    provider_urls = ['http://website.com', 'https://website-alternative.com']

    # two letters, used for showing what search engine each episode is from
    shortname = 'SE'

    # This should be set when you have built the complete search url
    # in the search method.  This information is used in the
    # `tvol config --test-se=...`
    url = ''

    # the search method will be called once with the show name, season
    # and episode.  If the search is a nondbshow search, the season
    # and episode won't be set.  The data that gets returned is an
    # array of arrays.  Each nested array is a search result that has
    # the data in this order:
    # [title, size, date, seeds, shortname, magneturl]
    def search(self, search_string, season=False, episode=False):

        self.url = 'search-site.com/search/all/{}/c/d/1/?fmt=rss'.format(
            search_string)
        show_data = []

        title = 'Mr.Robot.S02E03.HDTV.XviD-FUM[ettv]'
        size = '529.03 MB'
        date = '2016-07-21'
        seeds = '945'
        magnet = 'magnet:?xt=urn:btih:264886d841442158b3efc861bbfca5ef91d8f68b&dn=Mr.Robot.S02E01.720p.WEBRip.AAC2.0.H.264-KNiTTiNG%5Bettv%5D'
        show_data.append([title, size, date, seeds,
                          self.shortname, magnet])

        return show_data


if __name__ == '__main__':
    # some simple tests
    p = Provider()
    results = p.search('game of thrones', season=6, episode=6)
    click.echo(len(results))
