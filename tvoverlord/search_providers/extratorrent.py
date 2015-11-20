#!/usr/bin/env python

import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
from pprint import pprint as pp

import feedparser

from tvoverlord.util import U


class Provider(object):

    #provider_url = 'https://extratorrent.unblocked.la'
    #provider_url = 'http://extratorrent.cc'
    provider_url = 'http://195.144.21.16/'
    name = 'ExtraTorrent'

    @staticmethod
    def se_ep (season, episode, show_title):
        season_just = str (season).rjust (2, '0')
        episode = str (episode).rjust (2, '0')
        #fixed = '"%s S%sE%s" OR "%s %sx%s"' % (
            #show_title, season_just, episode, show_title, season, episode)
        fixed = '%s S%sE%s' % (
            show_title, season_just, episode)
        return fixed

    def search(self, search_string, season=False, episode=False):

        if season and episode:
            search_string = '%s' % (
                self.se_ep(
                    season, episode, search_string))

        query = search_string
        encoded_search = urllib.parse.quote(query)
        # cid=0 everything, cid=8 tv shows:
        url = '{}/rss.xml?type=search&cid=0&search=%s'.format(self.provider_url)
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
            size = U.pretty_filesize (show['size'])
            title = show['title']

            # the ExtraTorrent rss feed doesn't supply the magnet link, or any
            # usable links (They must be downloaded from the site).  But the
            # feed has the URN hash, so we can build a magnet link from that.
            magnet_url = 'magnet:?xt=urn:btih:{}&dn={}'
            magnet_hash = show['info_hash']
            magnet = magnet_url.format(magnet_hash, urllib.parse.quote(title))
            seeds = show['seeders']
            if seeds == '---':
                seeds = '0'

            show_data.append([
                title,
                size,
                date,
                seeds,
                magnet
            ])

        show_data.sort(key=lambda x: int(x[3]), reverse=True) # sort by seeds
        return [header] + [show_data]

    def download (self, chosen_show, destination, final_name):
        pass


if __name__ == '__main__':

    show = Provider()
    #results = show.search ('"doctor who (2005) 5x01" OR "doctor who 2005 s05e01"')
    #results = show.search ('"doctor who (2005) s05e01"')
    #results = show.search('drunk history s03e04')
    results = show.search('Gotham S02E01')
    pp(results)
