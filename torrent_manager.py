#!/usr/bin/env python

r'''
Usage:
  some-script [<arg1>] [<arg2>]

Options:
  -h --help     Show this help
  -v --version  Show the version number
'''

import os
import re
import sqlite3
import time
from docopt import docopt
from pprint import pprint as pp
import logging as l


# set up logging
this_file = os.path.splitext(os.path.basename(__file__))[0]
log_file = '{}.log'.format(this_file)
l.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s',
              datefmt='%Y-%m-%d %H:%M:%S',
              filename=log_file)


class WatchedTorrents:
    """
    1. Watch shows/ folder
    2. When new shows/ top level folder/file created add to list
    3. Check contents of each list item and wait for *.part files to be changed

    """

    def __init__(self, torrent_hash, filename):
        pass

    def transfer(self, destination, method='copy'):
        pass

    def change_name(self):
        pass

    def start_watcher(self, directory):
        pass


def main(args):
    print args
    l.error('This is an error')
    l.info ('This is a log')
    l.warn('This is a warning')
    #pass

if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main(args)

'''
[
  [
    ["Heroes Reborn S01E04", "https://extratorrent.unblocked.la/rss.xml?type=search&cid=0&search=Heroes%20Reborn%20S01E04"],
    ["Name", "Size", "Date", "Seeds"],
    [0, 10, 12, 6],
    ["<", ">", "<", ">"]
  ],
  [
    ["Heroes.Reborn.S01E04.HDTV.x264-KILLERS[ettv]", "306.75 MB", "Oct 09/2015", "39239", 0],

    ["Heroes.Reborn.S01E04.720p.HDTV.x264-KILLERS[EtHD]", "978.02 MB", "Oct 09/2015", "3242", 1],

    ["Heroes.Reborn.S01E04.HDTV.XviD-FUM[ettv]", "347.82 MB", "Oct 09/2015", "421", 2],

    ["Heroes.Reborn.S01E04.720p.HDTV.x264-KILLERS", "978.02 MB", "Oct 09/2015", "120", 3],

    ["Heroes Reborn S01E04 720p HDTV x265 HEVC 185MB - ShAaNiG", "184.98 MB", "Oct 09/2015", "22", 4],

    ["Heroes Reborn S01E04 720p HDTV x264-KILLERS", "978.03 MB", "Oct 09/2015", "1", 5]
  ]
]

[[["Lifes%20Too%20Short%20S01E01", "http://thepiratebay.se/search/ Lifes%20Too%20Short%20S01E01/0/7/0 Lifes%20Too%20Short%201x01/0/7/0 "], ["Name", "Size", "Date", "Seeds"], [0, 11, 12, 6], ["<", ">", "<", ">"]],
[["Lifes Too Short S01E01 HDTV XviD-RiVER [eztv]", "232.78\u00a0MiB", "11-11\u00a02011", "11", 0], ["Lifes.Too.Short.S01E01.HDTV.XviD-RiVER", "242.12\u00a0MiB", "11-10\u00a02011", "1", 1], ["Lifes.Too.Short.S01E01.HDTV.Subtitulado.Esp.SC.avi", "232.99\u00a0MiB", "04-01\u00a02013", "1", 2], ["Lifes Too Short S01E01 HDTV XviD-RiVER", "232.78\u00a0MiB", "11-11\u00a02011", "0", 3], ["Lifes Too Short S01E01 HDTV XviD-RiVER[ettv]", "232.78\u00a0MiB", "11-11\u00a02011", "0", 4]]]

[[["Lifes Too Short S01E03", "https://extratorrent.unblocked.la/rss.xml?type=search&cid=0&search=Lifes%20Too%20Short%20S01E03"], ["Name", "Size", "Date", "Seeds"], [0, 10, 12, 6], ["<", ">", "<", ">"]],
[
["Lifes Too Short 1x08 HDTV x264-FoV [eztv]", "423.44 MB", "Mar 31/2013", "36", 0],
["Lifes Too Short S01E01 HDTV XviD-RiVER[ettv]", "232.78 MB", "Nov 11/2011", "0", 1],
["Lifes Too Short for Tantric Sex 50 Shortcuts to Sexual Ecstasy by Kate Taylor", "39.83 KB", "Feb 03/2009", "0", 2]
]
]
'''
