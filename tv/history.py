#!/usr/bin/env python

r"""
Usage:
  tvopost (download|move) missing
  tvopost (download|move) all [DAYS]

Options:
  -h --help     Show this help
  -v --version  Show the version number
"""

import os
import re
import datetime
from dateutil import parser
from docopt import docopt
from pprint import pprint as pp

from tv.tvconfig import Config
from tv.db import DB
from tv.consoletable import ConsoleTable
from tv.consoleinput import ask_user
from tv.downloadmanager import DownloadManager
#from tv.tvutil import FancyPrint
from tv.util import U


class History:
    def __init__(self, criteria=1):
        self.db = DB()
        print type(criteria), criteria

        if criteria is None:
            criteria = 1

        if isinstance(criteria, int):
            sqldata = self.db.get_downloaded_days(criteria)
        elif isinstance(criteria, datetime.datetime):
            sqldata = self.db.get_downloaded_date(criteria)
        elif isinstance(criteria, str):
            sqldata = self.db.get_downloaded_title(criteria)


        self.sqldata = sqldata

    def episode(self, name, season, episode):
        seep = ''
        if season and episode:
            seep = ' S{0:0>2}E{1:0>2}'.format(season, episode)
        full = name + seep
        return full

    def exists(self, filename):
        ok = 76
        missing = 160
        #print filename
        if filename is None:
            return ''
        elif os.path.exists(filename):
            #filename = U.hi_color(filename, foreground=ok)
            filename = filename
        else:
            #filename = U.hi_color(filename, foreground=missing)
            #filename = U.effects(['strikeon'], filename)
            filename = U.effects(['blackf', 'strikeon'], filename)
        return filename

    def format_date(self, date):
        parsed = parser.parse(date)
        #print new
        new = parsed.strftime('%a %b/%d')
        #print date
        return new

    def show(self):
        for row in self.sqldata:
            date = self.format_date(row[0])
            name = U.snip(self.episode(row[1], row[4], row[5]), 25)
            name = name.ljust(25)
            filename = self.exists(row[2])
            print '%s %s %s' % (date, name, filename)

    def copy(self):
        title = 'Copy files to %s' % Config.tv_dir
        selected = self.display_list(title)

        torrent_hash = selected[3]
        torrent_dir, torrent_name = os.path.split(selected[2])

        DownloadManager(torrent_hash, torrent_dir, torrent_name, debug=True)

    def display_list(self, title):
        sqldata = self.sqldata
        data = [
            [
                'title',
                ['Date downloaded', 'Show name, episode', 'Local file'],
                [16, 25, 0],
                ['<', '<', '<']
            ],
            [[self.format_date(i[0]),
              self.episode(i[1], i[4], i[5]),
              self.exists(i[2]),
              i[3]] for i in sqldata]
        ]
        tbl = ConsoleTable(data)
        tbl.set_title(title)
        tbl.set_count(None)
        tbl.is_postdownload = True
        torrent_hash = tbl.generate()

        selected = [i for i in data[1] if torrent_hash in i][0]
        #print "{} selected".format(selected[1])

        return selected


    def main(self, args):
        days = args['DAYS']
        action = 'download' if args['download'] else 'move'
        if args['all']:
            sqldata = self.db.get_downloaded(days)
        elif args['missing']:
            sqldata = self.db.get_missing()

        data = [
            [
                'title',
                ['Date downloaded', 'Show name, episode', 'Local file'],
                [16, 25, 0],
                ['<', '<', '<']
            ],
            [[self.format_date(i[0]),
              self.episode(i[1], i[4], i[5]),
              self.exists(i[2]),
              i[3]] for i in sqldata]
        ]
        #pp([[i[4], i[5]] for i in sqldata])
        #pp (data)
        if action == 'download':
            title = 'Re-download selected show'
        else:
            title = 'Copy selected file to: {}'.format(Config.tv_dir)

        tbl = ConsoleTable(data)
        tbl.set_title(title)
        tbl.set_count(None)
        tbl.is_postdownload = True
        torrent_hash = tbl.generate()

        #pp(data)
        #print torrent_hash
        #selected = [i for i in data if torrent_hash in i]
        selected = [i for i in data[1] if torrent_hash in i][0]
        #pp(selected)
        print "{} selected".format(selected[1])

        '[r]e-download, [c]opy to "~/net1/dl/TV Shows/", or [q]uit:'

        if action == 'move':
            # hash path filename
            #DownloadManager(torrent_hash, torrent_dir, torrent_name)
            print(torrent_hash, torrent_dir, torrent_name)

        '''
        SELECT DATE(download_date) AS dt,
               COUNT(download_date)
        FROM tracking
        GROUP BY dt

        SELECT DATE(download_date) AS dt,
        	COUNT(download_date) AS count,
        	JULIANDAY(DATE('now')) - JULIANDAY(DATE(download_date)) AS days
        FROM tracking
        GROUP by dt

        '''


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    #print args
    main(args)
