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


def episode(name, season, episode):
    seep = ''
    if season and episode:
        seep = ' S{0:0>2}E{1:0>2}'.format(season, episode)
    full = name + seep
    return full

def exists(filename):
    ok = 76
    missing = 160
    print filename
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

def format_date(date):
    parsed = parser.parse(date)
    #print new
    new = parsed.strftime('%a %b/%d')
    #print date
    return new

def main(args):
    days = args['DAYS']
    action = 'download' if args['download'] else 'move'
    db = DB()
    if args['all']:
        sqldata = db.get_downloaded(days)
    elif args['missing']:
        sqldata = db.get_missing()

    data = [
        [
            'title',
            ['Date downloaded', 'Show name, episode', 'Local file'],
            [16, 25, 0],
            ['<', '<', '<']
        ],
        [[format_date(i[0]),
          episode(i[1], i[4], i[5]),
          exists(i[2]),
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

    print episode

    if action == 'move':
        # hash path filename
        DownloadManager(torrent_hash, torrent_dir, torrent_name, debug=args['--debug'])

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