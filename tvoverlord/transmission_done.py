#!/usr/bin/env python3

import click
import os
from pprint import pprint as pp
from tvoverlord.downloadmanager import DownloadManager


CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', is_flag=True, help='Output debug info')
def main(debug):
    """This script passes the enviroment variables from transmission to
    tvoverlord.

    Transmission exports these enviroment variables:

    \b
    X TR_TORRENT_DIR
    X TR_TORRENT_HASH
    X TR_TORRENT_NAME
      TR_APP_VERSION
      TR_TIME_LOCALTIME
      TR_TORRENT_ID

    This script uses the ones marked with an X.  This information is
    used to manage the torrent after its been downloaded.

    """
    try:
        torrent_dir = os.environ['TR_TORRENT_DIR']
        torrent_hash = os.environ['TR_TORRENT_HASH']
        torrent_name = os.environ['TR_TORRENT_NAME']
    except KeyError:
        print('Enviroment variables not set')
        exit(1)

    if debug:
        print('torrent_hash:', torrent_hash)
        print('torrent_dir:', torrent_dir)
        print('torrent_name:', torrent_name)

    DownloadManager(torrent_hash, torrent_dir,
                    torrent_name, debug=debug)


if __name__ == '__main__':
    main()
