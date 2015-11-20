#!/usr/bin/env python3

r'''
Usage:
  deluge_done.py [--debug] TORRENT_HASH TORRENT_NAME TORRENT_DIR

This script passes the enviroment variables
from deluge to tvoverlord.

The execute plugin is needed for this to work.
http://dev.deluge-torrent.org/wiki/Plugins/Execute

Options:
  -d --debug    Output debug info
  -h --help     Show this help
  -v --version  Show the version number
'''

from docopt import docopt
import os
from pprint import pprint as pp
from tvoverlord.downloadmanager import DownloadManager


def main(args):
    torrent_dir = args['TORRENT_DIR']
    torrent_hash = args['TORRENT_HASH']
    torrent_name = args['TORRENT_NAME']

    if args['--debug']:
        print('torrent_hash:', torrent_hash)
        print('torrent_dir:', torrent_dir)
        print('torrent_name:', torrent_name)

    DownloadManager(torrent_hash, torrent_dir, torrent_name, debug=args['--debug'])


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main(args)

