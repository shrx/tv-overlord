import os
import configparser
import shutil
import sqlite3
import click

from pprint import pprint as pp


class Config:
    def __init__(self):
        pass

    thetvdb_apikey = 'DFDB0A667C844513'
    use_cache = True

    config_filename = 'config.ini'
    user_dir = click.get_app_dir('tvoverlord')

    db_file = '%s/%s' % (user_dir, 'shows.sqlite3')
    user_config = '%s/%s' % (user_dir, config_filename)

    if not os.path.exists(user_dir):
        # create dir and config.ini
        os.makedirs(user_dir)
        app_home = os.path.join(os.path.dirname(os.path.realpath(__file__)))
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
                filename TEXT,
                destination TEXT
            );
            '''
        conn = sqlite3.connect(db_file)
        curs = conn.cursor()
        curs.executescript(sql)
        conn.commit()
        conn.close()
        print('The database and config.ini have been created in "{}"'.format(user_dir))
        print('Run "tv --help", or "tv addnew \'show name\'" to add shows.')
        exit()  # since there is nothing in the db

    cfg = configparser.ConfigParser(allow_no_value=True)
    cfg.read(user_config)

    # OPTIONAL FIELDS
    # [App Settings]
    ip = cfg.get('App Settings', 'ip')
    clean_torrents = True if cfg.get('App Settings', 'clean torrents') == 'yes' else False
    search_type = 'newsgroup' if cfg.get('App Settings', 'search type') == 'newsgroup' else 'torrent'

    # [File Locations]
    tv_dir = os.path.expanduser(cfg.get('File Locations', 'tv dir'))
    staging = os.path.expanduser(cfg.get('File Locations', 'staging'))


if __name__ == '__main__':
    c = Config()
    print(c.staging)
    pass
