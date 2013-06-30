#!/usr/bin/env python

import sys
from Util import U
from subprocess import call
from subprocess import Popen

from tv_config import config


class SearchError (Exception):

    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Search (object):

    def __init__(self, provider):

        mod_name = 'search_providers.' + provider
        mod = __import__(mod_name, fromlist=["Provider"])
        engine = getattr (mod, 'Provider')
        self.engine = engine()

        self.season = ''
        self.episode = ''
        self.show_name = ''


    #def se_ep (self, season, episode, both=True, show_title=''):
    #    season_just = str (season).rjust (2, '0')
    #    episode = str (episode).rjust (2, '0')
    #    if both:
    #        # fixed = 'S%sE%s | %sx%s' % (season_just, episode, season, episode)
    #        fixed = '"%s S%sE%s" OR "%s %sx%s"' % (
    #            show_title, season_just, episode, show_title, season, episode)
    #    else:
    #        fixed = 'S%sE%s' % (season_just, episode)
    #
    #    return fixed


    def search(self, search_string, season=False,
               episode=False):
        '''
        Return an array of values:

        [
          [
            [head1, head2, head3, id],
            [head1-width, head2-width, head3-width],
            [head1-alignment, head1-alignment, head1-alignment]
          ],
          [data from search...]
        ]
        '''

        self.season = season
        self.episode = episode
        self.show_name = search_string

        msg = 'Searching for: %s...' % (search_string)
        msg = U.hi_color (msg, foreground=16, background=184)
        sys.stdout.write (msg)
        sys.stdout.flush()
        backspace = '\b' * len (msg)
        overwrite = ' ' * len (msg)

        search_results = self.engine.search(search_string, season, episode)

        print '%s%s' % (backspace, overwrite)

        return search_results


    def download(self, chosen_show, destination):
        '''
        Pass the chosen show's data and destination to the providers
        download method and return the name of the file downloaded
        back to get-nzb.v2.py
        '''

        downloaded_filename = ''
        if chosen_show.startswith("magnet:"):

            # gvfs-... are the Gnome tools for interacting with
            # the file system.  Use KIO for kde.
            # gvfs-open will open whatever application is associated
            # with magnet links.
            Popen (["gvfs-open", chosen_show])
            # print chosen_show


        else:       # is a nzb file
            # for engine in self.engines:
            final_name = ''
            # only cleans name for tv show downloads
            # TODO: make work for 'nondbshow' also.
            if self.season and self.episode:
                cleaned_title = chosen_show.replace(
                    ' ', '_').replace('.', '_')
                nogo = '/\\"\'[]()#<>?!@$%^&*+='
                for c in nogo:
                    cleaned_title = cleaned_title.replace(c, '')

                final_name = '%s.%s.nzb' % (        # '%s.%s---%s.nzb'
                    self.show_name.replace(' ', '.'),
                    "S%sE%s" % (self.season.rjust(2, '0'), self.episode.rjust(2, '0'))
                    # self.se_ep(self.season, self.episode, both=False)
                    #, cleaned_title
                )
                print final_name
            downloaded_filename = self.engine.download (
                chosen_show, destination, final_name)

        return downloaded_filename


if __name__ == '__main__':

    test = Search ('nzbindex')
    test = Search ('NZBIndex')
    test = Search('x')
