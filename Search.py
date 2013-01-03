#!/usr/bin/env python


from get_nzb_config import config
from search_providers.NZBIndex import Provider as engine1
from search_providers.newsnet-crawler import Provider as engine2


class SearchError (Exception):

    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Search (object):

    def __init__(self):
        # self.engine1 = engine1()
        # self.engine2 = engine2()
        self.engines = [engine1(), engine2()]


    def config(self):
        pass


    def search(self, search_string, min_size=100, max_size=False):
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
          {nzbname: "American.Horror.Story.S01E01.FRENCH.BDRip.XviD-JMT.nfo" - 602,76 MB - yEnc",
           size: 592686000,
           usenet_date: 'Nov 05/2012'}
          {...}
          {...}
        ]

        '''

        all_results = []
        for engine in self.engines:
            search_results = self.engine1.search(search_string)
            all_results = all_results + search_results

        return all_results


    def download(self, chosen_show, destination):
        '''
        Pass the chosen show's data and destination to the providers
        download method and return the name of the file downloaded
        back to get-nzb.v2.py
        '''

        downloaded_filename = ''
        for engine in self.engines:
            if chosen_show['engine'] == engine.identity():
                downloaded_filename = engine.download (chosen_show, destination)

        return downloaded_filename


        # download_engine = chosen_show['engine']
        # downloaded_filename = self.engine1.download (chosen_show, destination)
        # return downloaded_filename


if __name__ == '__main__':

    test = Search ('nzbindex')
    test = Search ('NZBIndex')
    test = Search('x')
