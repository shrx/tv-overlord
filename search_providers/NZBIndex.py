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

    def search (self, search_string):
        '''
        Minimum age:	 days
        Sort by:         agedesc, age, sizedesc, size
        Minimum size:	 MB
        Maximum size:	 MB
        Default query:
        Poster:
        NFO content:
        Has NFO file
        Hide crossposts
        Show complete releases only  1
        Hide possible spam           1


        Searching
        ---------

        In the default search form you can enter search terms you would like
        to search for. After searching the results shown will match ALL search
        terms entered. For example, if you search for

        foo bar

        all search results will contain both 'foo' AND 'bar'.

        Instead of using ALL terms you can also search for only one (or a few)
        of the terms. To do this you need to use the '|' symbol. For example,
        to search for either 'foo' or 'bar' you can enter the search term

        foo | bar

        On some occasions you would like to exclude results with certain words
        from your search. For example, if you want the word 'foo', but not
        'bar' in your search results you can enter

        foo -bar

        The last option we offer is to search for a sentence that should match
        exactly. In case of 'foo bar' these two words will not necessarily
        turn up next to each other in the search results. If you would like to
        search for some group of words you can put double-quotes around the
        terms. When you need 'foo' and 'bar' to be next to each other the
        correct search would be:

        "foo bar"

        You can't use more than 20 keywords when searching.


nzbindex.com/rss/?q=arrow+s01e09&minage=1&sort=agedesc&minsize=100&maxsize=1000&complete=1&max=100&more=1

        '''


        search_template = 'http://nzbindex.com/rss/?q=%s&sort=agedesc&minsize=100&complete=1&max=25&more=1'
        return search_template

    def download (self):
        pass


if __name__ == '__main__':

    pass
