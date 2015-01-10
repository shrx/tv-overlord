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
l.basicConfig(format='%(asctime)s -- %(levelname)s -- %(message)s',
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
