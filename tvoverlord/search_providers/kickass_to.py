#!/usr/bin/env python

import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
import pprint

import feedparser

from tvoverlord.util import U


class Provider (object):
    #provider_url = 'http://kickass.to'
    #provider_url = 'http://thekat.tv'
    provider_url = 'http://kat.cr'
    name = 'Kickass Torrents'


    @staticmethod
    def se_ep (season, episode, show_title):
        season_just = str (season).rjust (2, '0')
        episode = str (episode).rjust (2, '0')
        fixed = '"%s" S%sE%s OR %sx%s' % (
            show_title, season_just, episode, season, episode)

        return fixed


    def search(self, search_string, season=False, episode=False):

        if season and episode:
            search_string = '%s' % (
                self.se_ep(
                    season, episode, search_string))

        query = search_string
        encoded_search = urllib.parse.quote (query)
        url = '{}/usearch/%s/?rss=1&field=seeders&sorder=desc'.format(self.provider_url)
        full_url = url % encoded_search

        parsed = feedparser.parse(full_url)
        header = [
            [search_string, full_url],
            ['Name', 'Size', 'Date', 'Seeds'],
            [0, 10, 12, 6],
            ['<', '>', '<', '>']]
        show_data = []

        for show in parsed['entries']:
            dt = datetime.fromtimestamp(mktime(show['published_parsed']))
            date = dt.strftime('%b %d/%Y')

            size = U.pretty_filesize (show['torrent_contentlength'])

            # title = U.snip (show['title'].ljust (title_w), title_w)
            # title = title.replace ('avi', U.fg_color ('green', 'avi'))
            title = show['title']

            show_data.append([
                title,                    # title
                size,                     # show size
                date,                     # date
                show['torrent_seeds'],    # seeds
                show['torrent_magneturi'] # id (download magnet url)
            ])

        #show_data.sort(key=lambda x: int(x[3]), reverse=True) # sort by seeds
        return [header] + [show_data]

    def download (self, chosen_show, destination, final_name):

        pass


if __name__ == '__main__':

    url = 'http://kickass.to/usearch/under%20the%20dome%20category%3Atv/?rss=1'

    show = Provider()

    results = show.search ('"doctor who (2005) 5x01" OR "doctor who 2005 s05e01"')

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint (results)

    '''
    torrent_magneturi
    id
    title_detail --- {'base': u'http://kickass.to/usearch/under%20the%20dome%20category%3Atv/?rss=1', 'type': u'text/plain', 'value': u'Under the Dome S01E01 720p HDTV X264-DIMENSION [eztv]', 'language': None}
    torrent_seeds
    torrent_contentlength --- 1252895269
    title --- Under the Dome S01E01 720p HDTV X264-DIMENSION [eztv]
    published_parsed --- time.struct_time(tm_year=2013, tm_mon=6, tm_mday=25, tm_hour=5, tm_min=45, tm_sec=2, tm_wday=1, tm_yday=176, tm_isdst=0)
    torrent_infohash --- DF4708C7E96E439FADDCD6F5BCD1A79503A1738C

    "doctor who (2005) 5x01" OR "doctor who 2005 s05e01"

    '''
