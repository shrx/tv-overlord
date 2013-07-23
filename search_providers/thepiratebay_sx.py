#!/usr/bin/env python

import urllib
import os
from time import mktime
from datetime import datetime
from bs4 import BeautifulSoup
import urllib2
import re
import pprint

from Util import U


class Provider (object):

    provider_url = 'http://thepiratebay.sx/'
    name = 'The Pirate Bay'

    def se_ep(self, show_title, season, episode):
        search_one = '%s S%sE%s' % (
            show_title,
            season.rjust(2, '0'),
            episode.rjust(2, '0'))

        search_two = '%s %sx%s' % (
            show_title,
            season,
            episode.rjust(2, '0'))

        return [search_one, search_two]


    def search(self, search_string, season=False, episode=False):

        header = [
            '%s  (%s)' % (search_string, self.provider_url),
            ['Name', 'Size', 'Date', 'Seeds'],
            [0, 11, 12, 6],
            ['<', '>', '<', '>']]
        show_data = []

        if season and episode:
            searches = self.se_ep(search_string, season, episode)
        else:
            searches = [search_string]

        for search in searches:
            search_string = urllib.quote(search)
            url = '%s/search/%s/0/7/0' % (self.provider_url, search_string)
            html = urllib2.urlopen(url)
            soup = BeautifulSoup(html)

            search_results = soup.find('table', id='searchResult')
            if not search_results:
                continue

            # for each row in search results table, (skipping thead)
            for tr in search_results.find_all('tr')[1:]:
                tds = tr.find_all('td')[1:]

                name = tds[0].find('a', {'class':'detLink'}).string

                details = tds[0].find('font').contents[0].split(', ')
                date = details[0].replace('Uploaded ', '')
                size = details[1].replace('Size ', '')

                magnet = tds[0].find('a', href=re.compile('magnet:.*')).attrs['href']
                seeds = tds[1].string

                show_data.append([name, size, date, seeds, magnet])

        return [header] + [show_data]



if __name__ == '__main__':

    pass
