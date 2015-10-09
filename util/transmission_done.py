#!/usr/bin/env python

r'''
Usage:
  transmission_done.py

This script passes the enviroment variables from transmission to
the torrent manager.

Options:
  -h --help     Show this help
  -v --version  Show the version number
'''

from docopt import docopt
import os
from pprint import pprint as pp
from torrent_manager import TorrentManager


# enviroment variables passed from transmission:
#
#  TR_APP_VERSION
#  TR_TIME_LOCALTIME
#x TR_TORRENT_DIR
#x TR_TORRENT_HASH
#  TR_TORRENT_ID
#x TR_TORRENT_NAME

def main():
    try:
        torrent_dir = os.environ['TR_TORRENT_DIR']
        torrent_hash = os.environ['TR_TORRENT_HASH']
        torrent_name = os.environ['TR_TORRENT_NAME']
    except KeyError:
        print 'Enviroment variables not set'
        exit()

    TorrentManager(torrent_hash, torrent_dir, torrent_name)


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main()

