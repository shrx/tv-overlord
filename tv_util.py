#!/usr/bin/env python

import os
import sys
import urllib2
import json

from Util import U
from tv_config import Config


class FancyPrint:
    def __init__(self):
        self.prev_fancy = False
        console_rows, console_columns = os.popen('stty size', 'r').read().split()
        self.bs = '\b' * int(console_columns)
        self.console_columns = int(console_columns)


    def standard_print(self, msg):
        msg = '\n'.join([i.ljust(self.console_columns) for i in msg.split('\n')])
        if self.prev_fancy:
            msg += '\n'
            self._back_print(msg)
        else:
            print msg
        self.prev_fancy = False


    def fancy_print(self, msg):
        msg = msg.ljust(self.console_columns)
        if self.prev_fancy:
            self._back_print(msg)
        else:
            sys.stdout.write(msg)
            sys.stdout.flush()
        self.prev_fancy = True


    def done(self, msg=''):
        msg = msg.ljust(self.console_columns)
        self._back_print(msg)


    def _back_print(self, msg):
        full_msg = '%s%s' % (self.bs, msg)

        sys.stdout.write(full_msg)
        sys.stdout.flush()


class RT:
    def __init__(self):
        self.api_key = Config.rt_apikey


    def search(self, title):
        url = 'api.rottentomatoes.com/api/public/v1.0/movies.json\
            ?q={title}&page_limit=50&page=1&apikey={key}'
        url = url.format(title=title, key=self.api_key)
        return self._get_data(url)


    def details(self, rt_id):
        url = 'api.rottentomatoes.com/api/public/v1.0/movies/{rt_id}.json\
            ?apikey={key}&_prettyprint=false'
        url = url.format(rt_id=rt_id, key=self.api_key)
        return self._get_data(url)


    def imdb_details(self, imdb_id):
        url = 'http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?type=imdb&id={imdb_id}&apikey={key}&_prettyprint=false'
        url = url.format(imdb_id=imdb_id, key=self.api_key)
        return self._get_data(url)


    def _get_data(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) \
            Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5'}
        request = urllib2.Request(url=url)

        # print url
        # response = urllib2.urlopen (request)
        # page = response.read()
        # print page

        try:
            response = urllib2.urlopen(request)
            page = response.read()
        except Exception:
            U.wr('ERROR: httplib.BadStatusLine')
            page = ''

        data = json.loads(page)
        return data





if __name__ == '__main__':

    pass

