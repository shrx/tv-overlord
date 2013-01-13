#!/usr/bin/env python


class Provider (object):

    provider_url = 'http://nzb.cc'
    name = 'nzb.cc'

    def __init__ (self):
        pass

    def search (self, search_string):
        pass

    def download (self, chosen_show, destination):
        pass
