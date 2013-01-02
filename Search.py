#!/usr/bin/env python


from get_nzb_config import config
from search_providers.NZBIndex import Provider as engine1


class SearchError (Exception):

    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Search (object):

    # providers = ['engine1']
    # provider = 'NZBIndex'
    # config = {
    #       'NZBMatrix': [username:'smmcg', apiKey:config.nzbmatrix_apikey]
    #     , 'NZBIndex': []
    # }

    def __init__(self, provider='NZBIndex', config=[]):
        # pass
        # print 'search_providers.%s' % provider
        #try:
        #    mod = __import__ ('search_providers.%s' % provider)
        #    print dir(mod)
        #    self.engine = mod.Provider
        #except ImportError:
        #    print '%s is not a valid search provider' % provider
        #    exit()


        # import search_providers.NZBIndex as enginex
        self.engine1 = engine1()


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



        search_results = self.engine1.search(search_string)
        return search_results


    def download(self, chosen_show, destination):
        '''
        Pass the chosen show's data and destination to the providers
        download method and return the name of the file downloaded
        back to get-nzb.v2.py
        '''

        downloaded_filename = self.engine1.download(chosen_show, destination)
        return downloaded_filename


if __name__ == '__main__':

    test = Search ('nzbindex')

    test = Search ('NZBIndex')

    test = Search('x')
