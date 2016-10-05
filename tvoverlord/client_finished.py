#!/usr/bin/env python3

import click
import os
import sys
import threading
from pprint import pprint as pp
from tvoverlord.config import Config
from tvoverlord.db import DB
from tvoverlord.downloadmanager import DownloadManager
from tvoverlord.tvol import __version__
from tvoverlord.db import Database
from tvoverlord.remote import Telemetry


CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


def telemetry(cmd):
    def remote():
        db2 = Database()
        db2.configure()
        te = Telemetry()
        if te.have_permission(db=db2):
            te.send(db=db2, cmd=cmd, version=__version__)

    th = threading.Thread(target=remote, group=None)
    th.start()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', is_flag=True, help='Output debug info')
@click.version_option(version=__version__)
def transmission(debug):
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
    Config.get_config_data()
    DB.configure()
    telemetry('transmission_done')

    try:
        torrent_dir = os.environ['TR_TORRENT_DIR']
        torrent_hash = os.environ['TR_TORRENT_HASH']
        torrent_name = os.environ['TR_TORRENT_NAME']
    except KeyError:
        sys.exit('Enviroment variables not set')

    if debug:
        click.echo('torrent_hash: %s' % torrent_hash)
        click.echo('torrent_dir: %s' % torrent_dir)
        click.echo('torrent_name: %s' % torrent_name)

    DownloadManager(torrent_hash, torrent_dir,
                    torrent_name, debug=debug)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('torrent_hash')
@click.argument('torrent_name')
@click.argument('torrent_dir')
@click.option('--debug', is_flag=True, help='Output debug info')
@click.version_option(version=__version__)
def deluge(torrent_hash, torrent_name, torrent_dir, debug):
    """Manage torrents downloaded by deluge.

    Deluge will call this script when the torrent has been downloaded.
    It will pass TORRENT_HASH, TORRENT_NAME and TORRENT_DIR as arguements.

    \b
    The execute plugin is needed for this to work.
    http://dev.deluge-torrent.org/wiki/Plugins/Execute
    """
    Config.get_config_data()
    DB.configure()
    telemetry('deluge_done')

    if debug:
        click.echo('torrent_hash: %s' % torrent_hash)
        click.echo('torrent_dir: %s' % torrent_dir)
        click.echo('torrent_name: %s' % torrent_name)

    DownloadManager(torrent_hash, torrent_dir,
                    torrent_name, debug=debug)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('info_hash')
@click.argument('torrent_name')
@click.argument('torrent_dir')
@click.option('--debug', is_flag=True, help='Output debug info')
@click.version_option(version=__version__)
def qbittorrent(info_hash, torrent_name, torrent_dir, debug):
    """Manage torrents downloaded by qBittorrent.

    \b
    In tools > options > downloads > Run external program
    Add: /absolute/path/to/qbittorrent_done %I %N %D
    """
    Config.get_config_data()
    DB.configure()
    telemetry('qbittorrent_done')

    if debug:
        click.echo('info_hash: %s' % info_hash)
        click.echo('torrent_dir: %s' % torrent_dir)
        click.echo('torrent_name: %s' % torrent_name)

    DownloadManager(info_hash, torrent_dir,
                    torrent_name, debug=debug)
