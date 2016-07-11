# uses rss
# http://www.torrentdownloads.me/rss.xml?type=search&search=Underground+S01E04

import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
import pprint
import click

import feedparser

from tvoverlord.util import U


class Provider():
    name = 'Torrent Downloads'
    provider_urls = ['http://www.torrentdownloads.me']
    url = ''
    short_name = 'TD'

    def search(self, search_string, season=False, episode=False):

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        # http://www.torrentdownloads.me/rss.xml?type=search&search=doctor+who+s05e01
        base_url = '%s/rss.xml?type=search&search={}' % self.provider_urls[0]
        show_data = []
        for search in searches:
            encoded_search = urllib.parse.quote(search)
            url = base_url.format(encoded_search)
            parsed = feedparser.parse(url)

            if len(parsed) == 0:
                continue

            for show in parsed['entries']:
                
                dt = datetime.fromtimestamp(mktime(show['published_parsed']))
                date = dt.strftime('%b %d/%Y')
                size = U.pretty_filesize(show['size'])
                title = show['title']
                seeds = show['seeders']
                magnet_url = 'magnet:?xt=urn:btih:{}&dn={}'
                magnet_hash = show['info_hash']
                magnet = magnet_url.format(magnet_hash, urllib.parse.quote(title))

                # torrentdownloads returns results that match any word in the
                # search, so the results end up with a bunch of stuff we aren't
                # interested in and we need to filter them out.
                stop = False
                for i in search.split(' '):
                    if i.lower() not in title.lower():
                        stop = True
                if stop:
                    continue
                
                show_data.append([
                    title,
                    size,
                    date,
                    seeds,
                    self.short_name,
                    magnet
                ])
                
        return show_data
            



    @staticmethod
    def se_ep(show_title, season, episode):
        season = str(season)
        episode = str(episode)
        search_one = '%s S%sE%s' % (
            show_title,
            season.rjust(2, '0'),
            episode.rjust(2, '0'))

        search_two = '%s %sx%s' % (
            show_title,
            season,
            episode.rjust(2, '0'))

        return [search_one, search_two]

