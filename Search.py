#!/usr/bin/env python

import sys
from Util import U

from get_nzb_config import config

##############################################################
from search_providers.NZBIndex_com import Provider as engine1
# from search_providers.nzb_cc import Provider as engine2
# from search_providers.nzbclub_com import Provider as engine1
##############################################################

class SearchError (Exception):

    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Search (object):

    def __init__(self):
        # self.engines = [engine1(), engine2()]
        self.engines = [engine1()]
        self.season = ''
        self.episode = ''
        self.show_name = ''


    def config(self):
        pass


    def se_ep (self, season, episode, both=True):
        season_just = str (season).rjust (2, '0')
        episode = str (episode).rjust (2, '0')
        if both:
            fixed = 'S%sE%s | %sx%s' % (season_just, episode, season, episode)
        else:
            fixed = 'S%sE%s' % (season_just, episode)

        return fixed


    def search(self, search_string, season=False, episode=False, min_size=100, max_size=False):
        '''
        Return an array of values:

        <nzbname> is the text used for display.
        <size> is the size of the download in bytes.
        <usenet_date> is the date in human readable form no wider that 12 characters.
        <nzbid> is an id or href that identifies the nzb file to download.  It will be
          passed to the download method.

        Example:
        --------
        [
          {nzbname: '"American.Horror.Story.S01E01.FRENCH.BDRip.XviD-JMT.nfo" - 602,76 MB - yEnc',
           size: 592686000,
           usenet_date: 'Nov 05/2012'}
          {...}
          {...}
        ]

        '''
        se = ''
        if (season and episode):
            self.season = season
            self.episode = episode
            self.show_name = search_string

            search_string = '%s %s' % (search_string, self.se_ep(season, episode, both=True))

        # print 'searching for:', search_string

        msg = 'Searching for: %s...' % (search_string)
        msg = U.hi_color (msg, foreground=16, background=184)
        sys.stdout.write (msg)
        sys.stdout.flush()
        backspace = '\b' * len (msg)
        overwrite = ' ' * len (msg)

        all_results = []
        for engine in self.engines:
            search_results = engine.search(search_string)
            all_results += search_results

        # print '>>>', all_results

        # done = U.hi_color (filename.ljust (len (msg)), foreground=34)#34
        print '%s%s' % (backspace, overwrite)

        return all_results


    def download(self, chosen_show, destination):
        '''
        Pass the chosen show's data and destination to the providers
        download method and return the name of the file downloaded
        back to get-nzb.v2.py
        '''

        # print chosen_show

        downloaded_filename = ''
        for engine in self.engines:
            if chosen_show['provider_name'] == engine.name:
                final_name = ''
                # only cleans name for tv show downloads
                # TODO: make work for 'nondbshow' also.
                if self.season and self.episode:
                    cleaned_title = chosen_show['nzbname'].replace(' ', '_').replace('.', '_')
                    nogo = '/\\"\'[]()#<>?!@$%^&*+='
                    for c in nogo:
                        cleaned_title = cleaned_title.replace(c, '')

                    final_name = '%s.%s.nzb' % (        # '%s.%s---%s.nzb'
                        self.show_name.replace(' ', '.')
                        , self.se_ep(self.season, self.episode, both=False)
                        #, cleaned_title
                    )
                downloaded_filename = engine.download (chosen_show, destination, final_name)

        return downloaded_filename


if __name__ == '__main__':

    test = Search ('nzbindex')
    test = Search ('NZBIndex')
    test = Search('x')
