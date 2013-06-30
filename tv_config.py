#!/usr/bin/env python
import os
import sys
import ConfigParser


class config:

    thetvdb_apikey = 'DFDB0A667C844513'
    rt_apikey = 'caxewwhecy767pye7zr3dfrb'
    use_cache = True

    config_filename = 'config.ini'
    user_config = os.path.join (
        os.environ ['HOME'],    # '/Users/sm/'
        '.tv-downloader',
        config_filename
    )

    user_config_exists = app_config_exists = True
    if not os.path.exists (user_config):
        print 'Config file does not exist: %s' % user_config
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
