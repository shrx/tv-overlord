
import os
import re
import sqlite3
import time
from pprint import pprint as pp
import logging as l
from tv_config import Config


class TorrentManager:

    def __init__(self, torrent_hash, path, filename):

        torrent_origin = Config.tv_dir

        # set up logging
        log_file = '{}/torrent_manager.log'.format(torrent_origin)
        l.basicConfig(format='%(asctime)s::%(levelname)s::%(message)s',
                      datefmt='%Y-%m-%d %H:%M:%S',
                      filename=log_file, level=l.DEBUG)

        l.info('hash:', torrent_hash)
        l.info('path:', path)
        l.info('filename:', filename)

        new_name = os.path.join(torrent_origin, filename)
        if Config.clean_torrents:
            new_name = self.change_name(torrent_hash)
            self.remove_garbage(new_name)

        if Config.torrent_done:
            self.transfer(new_name, Config.tv_dir, method=Config_torrent_done)



    def transfer(self, torrent_file, destination, method='copy'):

        pass

    def change_name(self, torrent_hash):
        new_name = ''
        # get info from db

        # rename files

        return new_name

    def remove_garbage(self, file_name):
        pass


