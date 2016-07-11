import sys
import subprocess
import os
import platform
import concurrent.futures
from pprint import pprint as pp
import socket
# from urllib.parse import urlparse
import urllib
import click

from tvoverlord.tvutil import style
from tvoverlord.config import Config

# torrent search engings
from tvoverlord.search_providers import extratorrent
from tvoverlord.search_providers import bitsnoop
from tvoverlord.search_providers import kickass_to
from tvoverlord.search_providers import thepiratebay_sx
from tvoverlord.search_providers import onethreethreesevenx_to
from tvoverlord.search_providers import torrentdownloads_me
from tvoverlord.search_providers import rarbg_to
from tvoverlord.search_providers import eztv_ag

# newsgroup search engines
from tvoverlord.search_providers import nzbclub_com
from tvoverlord.search_providers import nzbindex_com


class SearchError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Search(object):
    torrent_engines = [bitsnoop, extratorrent, thepiratebay_sx, kickass_to,
                       onethreethreesevenx_to, rarbg_to, eztv_ag]
    # , torrentdownloads_me # <-- a suspicious number of seeds

    # for nzb searches, only the first one listed will be used
    newsgroup_engines = [nzbclub_com]
    # , nzbindex_com # <-- rss feed not working

    def __init__(self):
        self.season = ''
        self.episode = ''
        self.show_name = ''

    def job(self, engine, search_string, season, episode):
        search = engine.Provider()
        search_results = search.search(search_string, season, episode)

        ## for info about each search
        # click.echo(search.name, len(search_results))

        return search_results

    def search(self, search_string, season=False,
               episode=False, search_type='torrent'):
        """
        Return an array of values:

        [
          [
            ['Title string', 'search url'],
            [head1, head2, head3, id],
            [head1-width, head2-width, head3-width],
            [head1-alignment, head2-alignment, head3-alignment]
          ],
          [
            [<column 1 data>, <column 2 data>, <column 3 data>, <id>],
            [<column 1 data>, <column 2 data>, <column 3 data>, <id>],
            # etc...
          ]
        ]
        """

        self.season = season
        self.episode = episode
        self.show_name = search_string
        self.search_type = search_type

        msg = 'Searching for: {0:s}...'.format(search_string)
        if Config.is_win:
            msg = style(msg, fg='black', bg='yellow')
        else:
            msg = style(msg, fg=16, bg=184)
        sys.stdout.write(msg)
        sys.stdout.flush()
        backspace = '\b' * len(msg)
        overwrite = ' ' * len(msg)

        if self.search_type == 'torrent':
            header = [
                [search_string, ''],
                ['Name', 'Size', 'Date', 'Seeds', 'SE'],
                [0, 10, 12, 6, 2],
                ['<', '>', '<', '>', '<']]
        else:
            header = [
                [search_string, ''],
                ['Name', 'Size', 'Date', 'SE'],
                [0, 10, 12, 2],
                ['<', '>', '<', '<']]

        if self.search_type == 'torrent':
            engines = self.torrent_engines
        else:
            engines = self.newsgroup_engines
            self.engine = engines[0]

        socket.setdefaulttimeout(3.05)
        episodes = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            res = {
                executor.submit(self.job, engine, search_string, season, episode): engine for engine in engines
            }
            for future in concurrent.futures.as_completed(res):
                results = future.result()
                episodes = episodes + results

        if self.search_type == 'torrent':

            episodes.sort(key=lambda x: int(x[3]), reverse=True)  # sort by seeds

            # Remove torrents with 0 seeds
            #for i, episode in enumerate(episodes):
            #    seeds = int(episode[3])
            #    click.echo(episode[0])
            #    if not seeds:
            #        click.echo('    ', seeds, episode[0])
            #        del episodes[i]

            # remove duplicates since different sites might have the same torrent
            titles = []
            for i, episode in enumerate(episodes):
                title = episode[0]
                if title in titles:
                    del episodes[i]
                else:
                    titles.append(title)

            # the following will remove duplicates based on the magnet hash
            hashes = []
            for i, episode in enumerate(episodes):
                o = urllib.parse.urlparse(episode[5])
                torrent_hash = urllib.parse.parse_qs(o.query)['xt']
                torrent_hash = torrent_hash[0].split(':')[-1]
                if torrent_hash in hashes:
                    del episodes[i]
                else:
                    hashes.append(torrent_hash)

        click.echo('%s%s' % (backspace, overwrite), nl=False)

        # return search_results
        return [header] + [episodes]

    def download(self, chosen_show, destination, search_type='torrent'):
        """
        Pass the chosen show's data and destination to the providers
        download method and return the name of the file downloaded
        back to get-nzb.v2.py
        """

        downloaded_filename = ''
        if chosen_show.startswith("magnet:"):

            if platform.system() == 'Linux':
                isX = True if os.environ.get('DISPLAY') else False
                if isX:
                    app = 'xdg-open'
                else:
                    sys.exit('\nNon X usage is not supported')

                try:
                    subprocess.Popen([app, chosen_show])
                except OSError:
                    sys.exit('\nYou do not have a bittorent client installed')
            elif platform.system() == 'Darwin':
                subprocess.Popen(["open", "--background", chosen_show])
            elif platform.system() == 'Windows':
                os.startfile(chosen_show)
            else:
                unknown_system = platform.platform()
                sys.exit('\nUnknown system:', unknown_system)

        else:  # is a nzb file
            final_name = ''
            # only cleans name for tv show downloads
            if self.season and self.episode:
                final_name = '%s.%s.nzb' % (
                    self.show_name.replace(' ', '.'),
                    "S%sE%s" % (self.season.rjust(2, '0'),
                                self.episode.rjust(2, '0'))
                )
                click.echo(final_name)
            downloader = self.engine.Provider()
            downloaded_filename = downloader.download(
                chosen_show, destination, final_name)

        return downloaded_filename


if __name__ == '__main__':
    test = Search('nzbindex')
    test = Search('NZBIndex')
    test = Search('x')
