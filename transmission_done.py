#!/usr/bin/env python3

r'''
Usage:
  transmission_done.py [--debug]

This script passes the enviroment variables from
transmission to tvoverlord.

Options:
  -d --debug    Output debut info
  -h --help     Show this help
  -v --version  Show the version number
'''

from docopt import docopt
import os
from pprint import pprint as pp
from tvoverlord.downloadmanager import DownloadManager


# enviroment variables passed from transmission:
#
#  TR_APP_VERSION
#  TR_TIME_LOCALTIME
#x TR_TORRENT_DIR
#x TR_TORRENT_HASH
#  TR_TORRENT_ID
#x TR_TORRENT_NAME

def main(args):
    try:
        torrent_dir = os.environ['TR_TORRENT_DIR']
        torrent_hash = os.environ['TR_TORRENT_HASH']
        torrent_name = os.environ['TR_TORRENT_NAME']
    except KeyError:
        print('Enviroment variables not set')
        exit()

    if args['--debug']:
        print('torrent_hash:', torrent_hash)
        print('torrent_dir:', torrent_dir)
        print('torrent_name:', torrent_name)

    DownloadManager(torrent_hash, torrent_dir, torrent_name, debug=args['--debug'])


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    main(args)

