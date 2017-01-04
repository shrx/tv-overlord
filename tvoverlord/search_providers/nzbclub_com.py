#!/usr/bin/env python

import urllib.request, urllib.parse, urllib.error
import socket
import os
import sys
from time import mktime
from datetime import datetime
from pprint import pprint as pp
import click

import feedparser

from tvoverlord.util import U


class Provider(object):
    provider_urls = ['http://www.nzbclub.com']
    name = 'NZBClub'
    shortname = 'NZ'

    @staticmethod
    def se_ep(season, episode, show_title):
        season_just = str(season).rjust(2, '0')
        episode = str(episode).rjust(2, '0')
        fixed = '%s S%sE%s or %s %sx%s' % (
            show_title, season_just, episode, show_title, season, episode)
        return fixed

    def search(self, search_string, season=False, episode=False, idx=None):

        """
        Default Search: Our default is prefix match
        Search 123 will match 123, 1234, 1234abcdefg
        Search 123 will not match 0123, ab123, ab123yz

        AND search:
        -----------
        the words hello and world:
        hello world

        NOT search:
        -----------
        the word hello but NOT the word world:
        hello -world

        We can't do NOT only search
        -world

        OR search:
        ----------
        the words hello or world:
        hello or world

        Each "or" is treated as new query part
        hello abcd or hello efgh != hello abcd or efgh

        grouping:
        ---------
        the exact phrase hello world:
        "hello world"
        """

        if season and episode:
            search_string = '%s' % (
                self.se_ep(
                    season, episode, search_string))

        url = '%s/nzbrss.aspx?' % self.provider_urls[0]
        query = {
            'q': search_string,
            'ig': 2,    # hide adult: 1=yes, 2=no
            'szs': 15,  # min size: 15=75m, 16=100m,
            'sze': 24,  # max size: 24=2gig
            'st': 5,    # sort.  5=relevence, 4=size (smallest first)
            'ns': 1,    # no spam
            'sp': 1,    # don't show passworded files
            'nfo': 0,   # has to have nfo  1=yes, 0=no
        }
        full_url = url + urllib.parse.urlencode(query)
        self.url = full_url

        parsed = feedparser.parse(full_url)

        header = [
            [search_string, full_url],
            ['Name', 'Date', 'Size'],
            [0, 12, 10],
            ['<', '<', '>']
        ]

        show_data = []
        for show in parsed['entries']:
            dt = datetime.fromtimestamp(mktime(show['published_parsed']))
            date = dt.strftime('%b %d/%Y')

            size = U.pretty_filesize(show['links'][0]['length'])

            nzbfile_url = show['links'][0]['href']
            nzbfile_url = nzbfile_url.replace(' ', '_')

            show_data.append([
                show['title'],
                size,
                date,
                self.shortname,
                '%s|%s' % (idx, nzbfile_url),
            ])

        return show_data


    def download(self, chosen_show, destination, final_name):
        """

        """

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

        # uncomment to test timeout errors:
        # socket.setdefaulttimeout(0.1)
        try:
            urllib.request.urlretrieve(href, fullname)
        except socket.timeout:
            click.echo()
            click.echo('Download timed out, try again.')
            sys.exit(1)
        except urllib.error.URLError:
            click.echo()
            click.echo('Download timed out, try again.')
            sys.exit(1)

        return filename


if __name__ == '__main__':
    pass
