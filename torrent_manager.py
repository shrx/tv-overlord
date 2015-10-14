
import os
import re
import sqlite3
import time
import datetime
import subprocess
import sys
from pprint import pprint as pp
import logging
from tv_config import Config
from DB import DB
from notify import Tell
import shutil


class TorrentManager(DB):
    """Manage media files after they have been downloaded

    A torrent client calls it's resprective manager; transmission_done.py
    or deluge_done.py; when the torrent has finished downloading, then
    that manager calls this class.

    This probably should just be functions instead of a class since its
    really just a singleton.

    Usage:
        TorrentManger(torrent_hash, path, filename, debug=False)

    Args:
        torrent_hash: The torrent hash, retrieved from the magnet url
        path:         The source folder where the downloaded torrent is
        filename:     The name of the torrent, can be a file or dir
        debug:        If console output is wanted

    Two settings in config.ini control behaviour
    torrent done: copy|move
    clean torrents: yes|no

    If 'torrent done' is not defined, then nothing happens. Else the
    content is copied or moved.

    if 'clean torrents' is 'yes', then only the media file is
    transfered.  If it's 'no', then whatever was downloaded is
    transfered to the destination.
    """
    def __init__(self, torrent_hash, path, filename, debug=False):
        torrent_origin = Config.torrents_dir
        # set up logging
        log_file = '{}torrent_manager.log'.format(torrent_origin)
        logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=log_file,
                            level=logging.DEBUG)

        if debug:
            console = logging.StreamHandler()
            formater = logging.Formatter('>>> %(message)s')
            console.setFormatter(formater)
            logging.getLogger('').addHandler(console)

        logging.info('-' * 50)
        logging.info('hash: %s', torrent_hash)
        logging.info('path: %s', path)
        logging.info('filename: %s', filename)

        if self.is_oneoff(torrent_hash):
            logging.info('Download is a one off. Doing nothing.')
            return

        filename = os.path.join(Config.torrents_dir, filename)
        if Config.torrent_done in ('copy', 'move'):
            if Config.clean_torrents:
                source = self.get_show_file(filename)

            pretty_filename, destination_dir = self.pretty_names(source, torrent_hash)
            destination_dir = os.path.join(Config.tv_dir, destination_dir)
            if not os.path.exists(destination_dir):
                os.mkdir(destination_dir)
                logging.info('creating dir: %s' % destination_dir)

            logging.info('copying %s to %s' % (source, destination_dir))
            self.copy(source, destination_dir)
            Tell('%s done' % pretty_filename)

        debug_command = '''export TR_TORRENT_NAME='%s'; export TR_TORRENT_DIR='%s'; export TR_TORRENT_HASH='%s'; python ~/projects/media-downloader/src/transmission_done.py'''
        logging.info(debug_command, filename, path, torrent_hash)

    def copy(self, source, destination):
        """Copy files or dirs using the platform's copy tool"""
        cmd = None
        if sys.platform.startswith(('darwin', 'linux')):
            cmd = ['cp', '-r', source, destination]
        elif sys.platform.startswith('win'):
            cmd = ['xcopy', source, destination, '/K/O/X']

        subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def pretty_names(self, filename, torrent_hash):
        """Generate a file name and dir name based on data from the database

        Args:
            filename - the dir or file that the new name will be based on
                It is used to get the file extention and and determine if
                it's a dir or not.
            torrent_hash - the hash is used to look up the data in the db

        Returns:
            Returns two values, a generated filename and a generated dir name
        """
        show_name, season, episode = self.get_show_info(torrent_hash)

        # new file name
        file_show_name = show_name.replace(' ', '.')
        seep = ''
        if season and episode:
            season = season.rjust(2, '0')
            episode = episode.rjust(2, '0')
            seep = 'S{}E{}'.format(season, episode)
        else:
            seep = datetime.date.today().isoformat()

        file_type = ''
        if os.path.isfile(filename):
            file_type = os.path.splitext(filename)[1]

        pretty_filename = '{}.{}{}'.format(file_show_name, seep, file_type)

        # new dir name
        pretty_dirname = show_name #.replace(' ', '_')

        #print '>>>', pretty_filename, pretty_dirname
        logging.info('Pretty names: %s, %s' % (pretty_filename, pretty_dirname))
        return pretty_filename, pretty_dirname

    def get_show_file(self, name):
        """Find the largest file in a dir

        If name is a file, just return that name, else
        return the name of the largest file

        Args:
            name - The name of a dir or file

        Returns:
            Returns the name of the largest file
        """
        if os.path.isfile(name):
            logging.info('{} is a file'.format(name))
            return name
        files_sizes = []
        for root, dirs, files in os.walk(name):
            for filename in files:
                full_filename = os.path.join(root, filename)
                size = os.stat(full_filename).st_size
                files_sizes.append([size, full_filename])
        files_sizes.sort(key=lambda torrent: int(torrent[0]), reverse=True)
        #pp(files_sizes)
        return files_sizes[0][1]






