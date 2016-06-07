#!/usr/bin/env python3

import click
from pprint import pprint as pp
from tvoverlord.downloadmanager import DownloadManager


CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('torrent_hash', type=int)
@click.argument('torrent_name')
@click.argument('torrent_dir')
@click.option('--debug', is_flag=True, help='Output debug info')
def main(torrent_hash, torrent_name, torrent_dir, debug):
    """Manage torrents downloaded by deluge.

    Deluge will call this script when the torrent has been downloaded.
    It will pass TORRENT_HASH, TORRENT_NAME and TORRENT_DIR as arguements.

    \b
    The execute plugin is needed for this to work.
    http://dev.deluge-torrent.org/wiki/Plugins/Execute
    """

    if debug:
        print('torrent_hash:', torrent_hash)
        print('torrent_dir:', torrent_dir)
        print('torrent_name:', torrent_name)

    DownloadManager(torrent_hash, torrent_dir,
                    torrent_name, debug=debug)


if __name__ == '__main__':
    main()
