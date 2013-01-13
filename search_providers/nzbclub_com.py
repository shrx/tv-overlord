#!/usr/bin/env python

import feedparser
import urllib
import os
from time import mktime
from datetime import datetime


class Provider (object):

    provider_url = 'http://www.nzbclub.com/'
    name = 'NZBClub'


    def search(self, search_string):

        # http://www.nzbclub.com/nzbfeed.aspx?q=cougar%20town%20s04e01&ig=2&szs=14&sze=24&st=1&ns=1
        # http://www.nzbclub.com/nzbfeed.aspx?q=cougar%20town%20s04e01&ig=2&szs=14&sze=24&st=5&ns=1

        url = 'http://www.nzbclub.com/nzbfeed.aspx?'
        query = {
            'q': search_string
            , 'ig': 2
            , 'szs': 1
            , 'sze': 24
            , 'st': 1
            , 'ns': 1   # no spam
            }
        full_url = url + urllib.urlencode (query)

        parsed = feedparser.parse(full_url)

        show_data = []
        for show in parsed['entries']:

            dt = datetime.fromtimestamp(mktime(show['published_parsed']))
            date = dt.strftime('%b %d/%Y')

            show_data.append({
                'nzbname': show['title']
                , 'usenet_date': date
                , 'size': show['links'][0]['length']
                , 'nzbid': show['links'][0]['href']
                , 'search_string': search_string
                , 'provider_name': Provider.name # In this case: NZBClub
                })

        # print 'show_data:', show_data
        # print 'shows:', len(show_data)
        return show_data


    def download (self, chosen_show, destination, final_name):
        '''

        '''
        # print '>>>chosen_show, destination, final_name', chosen_show, destination, final_name
        if not os.path.isdir (destination):
            raise ProviderError ('%s is not a dir' % (dest))

        href = chosen_show['nzbid']
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

        urllib.urlretrieve(href, fullname)

        return filename

if __name__ == '__main__':

    pass
