#!/usr/bin/env python
import os
import ConfigParser
import shutil
import sqlite3

from pprint import pprint as pp
from tv.consoleinput import ask_user as ask


class Config:
    def __init__(self):
        pass


    thetvdb_apikey = 'DFDB0A667C844513'
    rt_apikey = 'caxewwhecy767pye7zr3dfrb'
    use_cache = True

    config_filename = 'config.ini'
    user_dir = os.path.join(
        os.environ['HOME'],  # '/Users/sm/'
        '.tv-downloader'
    )
    user_db = '%s/%s' % (user_dir, 'shows.sqlite3')
    user_config = '%s/%s' % (user_dir, config_filename)

    if not os.path.exists(user_dir):
        print 'Config directory does not exist: %s' % user_dir
        if ask('Create config directory and files? [y/n]') == 'y':
            # create dir and config.ini
            os.mkdir(user_dir)
            app_home = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
            app_config = '%s/%s' % (app_home, config_filename)
            shutil.copy(app_config, user_dir)
            # make db
            sql = '''
                CREATE TABLE shows (
                    search_engine_name TEXT,
                    network_status TEXT,
                    status TEXT,
                    thetvdb_series_id TEXT,
                    name TEXT,
                    season NUMERIC,
                    episode NUMERIC,
                    next_episode TEXT,
                    airs_time TEXT,
                    airs_dayofweek TEXT,
                    ragetv_series_id TEXT
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
                    filename TEXT
                );
                '''
            conn = sqlite3.connect(user_db)
            curs = conn.cursor()
            curs.execute(sql)
            conn.commit()
            conn.close()
            print 'Run tv --help, or tv addnew "show name" to add shows.'
            exit()  # since there is nothing in the db
        else:
            exit()

    defaults = {'ip':False, 'clean torrents':False, 'tv dir':False,
                'torrents dir':False, 'torrent done':False}
    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read(user_config)

    # OPTIONAL FIELDS
    # [App Settings]
    ip = cfg.get('App Settings', 'ip')
    torrent_done = cfg.get('App Settings', 'torrent done')
    clean_torrents = cfg.get('App Settings', 'clean torrents')

    # [File Locations]
    tv_dir = os.path.expanduser(cfg.get('File Locations', 'tv dir'))
    torrents_dir = os.path.expanduser(cfg.get('File Locations', 'torrents dir'))

    # REQUIRED FIELDS
    providers = []
    try:
        # [File Locations]
        db_file = os.path.expanduser(cfg.get('File Locations', 'db file'))
        staging = os.path.expanduser(cfg.get('File Locations', 'staging'))

        # [Search Providers]
        for i in cfg.items('Search Providers'):
            providers.append(i[0])

        # [The Pirate Bay Settings]
        pirateurl = cfg.get('The Pirate Bay Settings', 'url')

    except ConfigParser.NoSectionError as err_msg:
        print err_msg, "in config file"
        exit()
    except ConfigParser.NoOptionError as err_msg:
        print err_msg, "in config file"
        exit()


if __name__ == '__main__':
    pass
