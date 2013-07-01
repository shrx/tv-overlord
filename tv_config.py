#!/usr/bin/env python
import os
import sys
import ConfigParser
import shutil
import sqlite3

from ConsoleInput import ask_user as ask


class config:

    thetvdb_apikey = 'DFDB0A667C844513'
    rt_apikey = 'caxewwhecy767pye7zr3dfrb'
    use_cache = True

    config_filename = 'config.ini'
    user_dir = os.path.join (
        os.environ ['HOME'],    # '/Users/sm/'
        '.tv-downloader'
    )

    user_config = '%s/%s' % (user_dir, config_filename)

    if not os.path.exists (user_dir):
        print 'Config directory does not exist: %s' % user_dir
        if ask ('Create config directory and files? [y/n]') == 'y':
            # create dir and config.ini
            os.mkdir(user_dir)
            app_home = os.path.dirname(os.path.realpath(__file__))
            app_config = '%s/%s' % (app_home, config_filename)
            shutil.copy(app_config, user_dir)
            # make db
            sql = '''
                CREATE TABLE shows (
                    search_engine_name TEXT,
                    network_status TEXT,
                    status TEXT, thetvdb_series_id TEXT,
                    name TEXT,
                    season NUMERIC,
                    episode NUMERIC,
                    ragetv_series_id TEXT
                );'''
            conn = sqlite3.connect ('%s/%s' % (user_dir, 'shows.sqlite3'))
            curs = conn.cursor()
            curs.execute (sql)
            conn.commit()
            conn.close()
            print 'Run tv --help, or tv addnew "show name" to add shows.'
            exit() # since there is nothing in the db
        else:
            exit()

    cfg = ConfigParser.ConfigParser(allow_no_value=True)
    cfg.read (user_config)


    providers = []
    try:
        # [File Locations]
        db_file = os.path.expanduser (cfg.get ('File Locations', 'db file'))
        staging = os.path.expanduser (cfg.get ('File Locations', 'staging'))

        # [Search Providers]
        for i in cfg.items('Search Providers'):
            providers.append(i[0])

    except ConfigParser.NoSectionError as err_msg:
        print err_msg, "in config file"
        exit()
    except ConfigParser.NoOptionError as err_msg:
        print err_msg, "in config file"
        exit()


if __name__ == '__main__':
    pass
