import os
import sys
import platform
import configparser
import shutil
import sqlite3
import click
import shlex
import types

from pprint import pprint as pp


class Config:
    def __init__(self):
        pass

    is_win = False
    if platform.system() == 'Windows':
        is_win = True

    thetvdb_apikey = 'DFDB0A667C844513'
    use_cache = True

    user_dir = click.get_app_dir('tvoverlord')
    db_file = os.path.join(user_dir, 'shows.sqlite3')
    config_filename = 'config.ini'
    user_config = os.path.join(user_dir, 'config.ini')

    console_columns, console_rows = click.get_terminal_size()
    console_columns = int(console_columns)
    if is_win:
        # On windows, columns are 1 char too wide
        console_columns = console_columns - 1

    # progressbar settings
    pb = types.SimpleNamespace()
    pb.width = 50
    if console_columns < 90:
        pb.width = 30
    if console_columns < 80:
        pb.width = 20
    if is_win:
        pb.light = 'green'
        pb.dark = 'blue'
    else:
        pb.light = 35
        pb.dark = 23
    pb.empty_char = ' '
    pb.fill_char = '*'
    pb.template = '%(label)s %(bar)s %(info)s'

    # number of ip address octets to match to be considered ok.  Must
    # be between 1 and 4
    parts_to_match = 3

    _msg = ''
    # create app config dir
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        _msg += 'App config dir created'
        _msg += '  %s' % user_dir

    # create config.ini
    if not os.path.exists(user_config):
        app_home = os.path.join(os.path.dirname(os.path.realpath(__file__)))
        app_config = os.path.join(app_home, config_filename)
        shutil.copy(app_config, user_dir)
        _msg += 'config.ini created'
        _msg += '  %s' % os.path.join(user_dir, config_filename)

    # create db
    if not os.path.exists(db_file):
        sql = '''
            CREATE TABLE shows (
                name TEXT,
                search_engine_name TEXT,
                display_name TEXT,
                date_added TEXT,
                network_status TEXT,
                status TEXT,
                thetvdb_series_id TEXT,
                ragetv_series_id TEXT,
                imdb_series_id TEXT,
                alt_series_id TEXT,
                season NUMERIC,
                episode NUMERIC,
                next_episode TEXT,
                airs_time TEXT,
                airs_dayofweek TEXT,
                rating TEXT,
                notes TEXT,
            );
            CREATE TABLE tracking (
                download_date TEXT,
                show_title TEXT,
                season TEXT,
                episode TEXT,
                download_data TEXT,
                chosen TEXT,
                chosen_hash TEXT,
                one_off INTERGER,
                complete INTERGER,
                filename TEXT,
                destination TEXT
            );
            '''
        conn = sqlite3.connect(db_file)
        curs = conn.cursor()
        curs.executescript(sql)
        conn.commit()
        conn.close()
        _msg += 'Database has been created'
        _msg += '  %s' % db_file

    if _msg:
        click.secho('-' * console_columns, fg='yellow')
        click.echo(_msg)
        click.secho('-' * console_columns, fg='yellow')

    categories = types.SimpleNamespace()
    categories.resolution = [
            '1080p', '1080i', '720p', '720i', 'hr', '576p',
            '480p', '368p', '360p']
    categories.sources = [
            'bluray', 'remux', 'dvdrip', 'webdl', 'hdtv', 'bdscr',
            'dvdscr', 'sdtv', 'webrip', 'dsr', 'tvrip', 'preair',
            'ppvrip', 'hdrip', 'r5', 'tc', 'ts', 'cam', 'workprint']
    categories.codecs = [
            '10bit', 'h265', 'h264', 'x264', 'xvid', 'divx']
    categories.audio = [
            'truehd', 'dts', 'dtshd', 'flac', 'ac3', 'dd5.1', 'aac', 'mp3']

    cfg = configparser.ConfigParser(allow_no_value=True, interpolation=None)
    cfg.read(user_config)

    # Settings from config.ini ---------------------------------
    # [App Settings]
    try:
        ip = cfg.get('App Settings', 'ip whitelist')
        # split, strip, and remove empty values from whitelist
        ip = [i.strip() for i in ip.split(',') if i.strip()]
    except configparser.NoOptionError:
        ip = None

    try:
        single_file = True if cfg.get('App Settings', 'single file') == 'yes' else False
    except configparser.NoOptionError:
        single_file = False

    try:
        template = cfg.get('App Settings', 'template')
    except configparser.NoOptionError:
        template = False

    try:
        search_type = 'newsgroup' if cfg.get('App Settings', 'search type') == 'newsgroup' else 'torrent'
    except configparser.NoOptionError:
        search_type = 'torrent'

    try:
        client = cfg.get('App Settings', 'client')
        client = shlex.split(client)
    except configparser.NoOptionError:
        client = None

    try:
        magnet_dir = cfg.get('App Settings', 'magnet folder')
    except configparser.NoOptionError:
        magnet_dir = None

    # [File Locations]
    try:
        tv_dir = os.path.expanduser(cfg.get('File Locations', 'tv dir'))
    except configparser.NoOptionError:
        tv_dir = None
    try:
        staging = os.path.expanduser(cfg.get('File Locations', 'staging'))
    except configparser.NoOptionError:
        staging = None

if __name__ == '__main__':
    c = Config()
    click.echo(c.staging)
    pass
