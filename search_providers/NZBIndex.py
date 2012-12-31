#!/usr/bin/env python

import feedparser


class NZBIndexError (Exception):

    def __init__ (self, value):
        self.value = value

    def __str__ (self):
        return repr(self.value)


class NZBIndex:

    def __init__ (self):
        pass

    def Search (self, search_string):
        search_template = 'http://nzbindex.com/rss/?q=%s&sort=agedesc&minsize=100&complete=1&max=25&more=1'

    def Download (self):
        pass


if __name__ == '__main__':

    pass
