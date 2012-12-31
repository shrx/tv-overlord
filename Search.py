#!/usr/bin/env python


from get_nzb_config import config


class SearchError (Exception):

    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class Search:

    providers = ['NZBMatrix', 'NZBIndex']
    # provider = 'NZBIndex'
    # config = {
    #       'NZBMatrix': [username:'smmcg', apiKey:config.nzbmatrix_apikey]
    #     , 'NZBIndex': []
    # }

    def __init__(self, provider='NZBIndex', config=[]):

        try:
            self.engine = __import__ ('search_providers.%s' % provider)
        except ImportError:
            print '%s is not a valid search provider' % provider
            exit()

    def config():
        pass

    def search(search_string, min_size=100, max_size=False):
        return self.engine.search(search_string)

    def download(nzb_id, destination):
        self.engine.download(nzb_id, destination)


if __name__ == '__main__':

    test = Search ('nzbindex')

    test = Search ('NZBIndex')

    test = Search('x')
