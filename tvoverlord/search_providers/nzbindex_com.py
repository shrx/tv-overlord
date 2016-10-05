#!/usr/bin/env python

import urllib.request, urllib.parse, urllib.error
import os
import sys
from time import mktime
from datetime import datetime
from pprint import pprint as pp
import click

import feedparser

from tvoverlord.util import U


class ProviderError(Exception):
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)


class Provider(object):
    # def __init__ (self):
    # pass

    provider_urls = ['http://nzbindex.com']
    name = 'NZBIndex'
    shortname = 'NI'


    @staticmethod
    def se_ep(season, episode, show_title):
        season_just = str(season).rjust(2, '0')
        episode = str(episode).rjust(2, '0')
        fixed = '%s S%sE%s | %sx%s' % (
            show_title, season_just, episode, season, episode)
        return fixed


    def search(self, search_string, season=False, episode=False):
        """
        Search options:
        ---------------
        Minimum age:	 days
        Sort by:         agedesc, age, sizedesc, size
        Minimum size:	 MB
        Maximum size:	 MB
        Default query:
        Poster:
        NFO content:
        Has NFO file
        Hide crossposts
        Show complete releases only  1
        Hide possible spam           1


        Searching
        ---------

        In the default search form you can enter search terms you would like
        to search for. After searching the results shown will match ALL search
        terms entered. For example, if you search for

        foo bar

        all search results will contain both 'foo' AND 'bar'.

        Instead of using ALL terms you can also search for only one (or a few)
        of the terms. To do this you need to use the '|' symbol. For example,
        to search for either 'foo' or 'bar' you can enter the search term

        foo | bar

        On some occasions you would like to exclude results with certain words
        from your search. For example, if you want the word 'foo', but not
        'bar' in your search results you can enter

        foo -bar

        The last option we offer is to search for a sentence that should match
        exactly. In case of 'foo bar' these two words will not necessarily
        turn up next to each other in the search results. If you would like to
        search for some group of words you can put double-quotes around the
        terms. When you need 'foo' and 'bar' to be next to each other the
        correct search would be:

        "foo bar"

        You can't use more than 20 keywords when searching.



        Top level of data structure returned from NZBIndex:
        ---------------------------------------------------
        bozo        ?
        encoding    u'UTF-8'
        entries     all shows                           results['entries'][0...x]
        feed        info about the feed                 results['feed']
        headers
        href        the rss link for these results
        namespaces  ?
        status      200
        version     u'rss20'
        """

        # search_template = ('nzbindex.com/rss/?q=%s&minage=%s&sort=%s' +
        # '&minsize=%s&maxsize=%s&complete=%s&max=%s&more=1')

        if season and episode:
            search_string = '%s' % (
                self.se_ep(
                    season, episode, search_string))

        url = 'http://nzbindex.com/rss/?'
        query = {
            'q': search_string,
            'minage': '0',
            'sort': 'agedesc',  # age, agedesc, size, sizedesc
            'minsize': '100',   # mb
            'maxsize': '5000',  # mb
            'complete': '1',  # return only complete posts
            'max': '100',  # results per page
            'more': '1',
        }

        full_url = url + urllib.parse.urlencode(query)

        # print 'searching...'
        parsed = feedparser.parse(full_url)

        show_data = []
        for show in parsed['entries']:
            dt = datetime.fromtimestamp(mktime(show['published_parsed']))
            date = dt.strftime('%b %d/%Y')

            size = U.pretty_filesize(show['links'][1]['length'])

            show_data.append([
                show['title'],
                size,
                date,
                self.shortname,
                show['links'][1]['href'],
            ])

        header = [
            #'%s  (%s)' % (search_string, self.provider_url),
            [search_string, full_url],
            ['Name', 'Date', 'Size'],
            [0, 12, 10],
            ['<', '<', '>']
        ]

        pp(show_data)
        return show_data


    def download(self, chosen_show, destination, final_name):
        if not os.path.isdir(destination):
            sys.exit('\n%s does not exist' % destination)

        href = chosen_show
        filename = href.split('/')[-1]
        if final_name:
            # final_name should be a name that SABNzbd can parse
            # if this is being used, it means that this download is
            # a tv show with a season and episode.
            fullname = destination + '/' + final_name
        else:
            # if NOT final_name, then this download came from
            # nondbshow, and is not associated with a tv show.
            # Could be a movie or one off download.
            fullname = destination + '/' + filename

        urllib.request.urlretrieve(href, fullname)

        return filename


if __name__ == '__main__':
    pass
