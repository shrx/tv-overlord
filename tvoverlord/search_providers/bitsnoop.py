#!/usr/bin/env python

import urllib.request, urllib.parse, urllib.error
from time import mktime
from datetime import datetime
from pprint import pprint as pp

import feedparser

from tvoverlord.util import U


class Provider(object):

    provider_url = 'http://bitsnoop.com/'
    name = 'BitSnoop'

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
        #http://bitsnoop.com/search/all/supernatural+s01e01+OR+1x01/c/d/1/?fmt=rss

        if season and episode:
            search_string = '%s' % (
                self.se_ep(
                    season, episode, search_string))

        query = search_string
        encoded_search = urllib.parse.quote(query)
        url = 'http://bitsnoop.com/search/all/{}/c/d/1/?fmt=rss'
        full_url = url.format(encoded_search)

        parsed = feedparser.parse(full_url)
        header = [
            [search_string, full_url],
            ['Name', 'Size', 'Date', 'Seeds'],
            [0, 10, 6, 6],
            ['<', '>', '=', '>']]
        show_data = []

        for show in parsed['entries']:
            #pp(show)

            if show['published_parsed']:
                dt = datetime.fromtimestamp(mktime(show['published_parsed']))
                date = dt.strftime('%b %d/%Y')
            else:
                date = '-'
            size = U.pretty_filesize (show['size'])
            title = show['title']
            seeds = show['numseeders']
            magnet = show['magneturi']

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

