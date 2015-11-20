
"""
Build a table to display data in a terminal.
"""

import os, string
from collections import namedtuple
from pprint import pprint as pp

from tvoverlord.consoleinput import ask_user
from tvoverlord.util import U


class ConsoleTable:
    def __init__(self, data):
        """Build a table to display data in the terminal

        @param data: An array of arrays.
        data must be in this format::

          [
            # TABLE DESCRIPTION LIST:
            [
              ['Title string', 'search url'],        # title string
              ['title', 'title', 'title', 'title'],  # titles of columns
              [10, 5, 0, 20],                        # widths of columns, 0 is flex
              ['<', '>', '=', '>']                   # alignments
            ],

            # TABLE DATA LIST.  Last one is what gets returned
            # after the user selects a row.
            [
              ['first', 'second', 'third', 'forth', 'key field'],
              ['first', 'second', 'third', 'forth', 'key field'],
              ['first', 'second', 'third', 'forth', 'key field']
            ]
          ]
        """
        console_rows, console_columns = os.popen('stty size', 'r').read().split()
        self.console_columns = int(console_columns)
        self.colors = {
            'title_fg': None,
            'title_bg': 19,
            'header_fg': None,
            'header_bg': 17,
            'body_fg': 'white',
            'body_bg': None,
            'bar': 19,
        }
        self.display_count = 5
        self.is_postdownload = False

        # Unpack the data param into more a usable format using namedtuples
        table = namedtuple('TableData', ['title', 'header', 'body'])
        table.title = namedtuple('TitleData', ['text'])
        table.header = namedtuple('HeaderData', ['titles'])
        table.header = namedtuple('HeaderData', ['widths'])
        table.header = namedtuple('HeaderData', ['alighnments'])
        table.body = namedtuple('BodyData', ['body'])

        table.title.text = data[0][0]
        table.header.titles = data[0][1]
        table.header.widths = data[0][2]
        table.header.alignments = data[0][3]
        table.body = data[1]

        self.table = table
        self.chosen_value = False

    def set_count(self, val):
        self.display_count = val

    def set_title(self, text):
        self.table.title.text = text

    def set_header(self, header_items):
        self.table.header.titles = header_items

    def set_colors(self, colors):
        self.colors = colors

    def generate(self):
        title_bar = U.hi_color(
            '|',
            foreground=self.colors['bar'],
            background=self.colors['header_bg']
        )
        bar = U.hi_color(
            '|',
            foreground=self.colors['bar']
        )

        # TITLE --------------------------------------------
        titletext = ('  ' + self.table.title.text).ljust(self.console_columns)
        title = U.effects(['boldon'], U.hi_color(
            titletext,
            foreground=self.colors['title_fg'],
            background=self.colors['title_bg'],
        ))
        print(title)

        # HEADER ROW ---------------------------------------
        header = self.table.header
        header_row = [U.hi_color(' ',     # the number/letter column
                                 background=self.colors['header_bg'],
                                 foreground=self.colors['header_fg'])]
        NUMBER_SPACE = 1
        BAR_COUNT = len(header.widths)
        flex_width = self.console_columns - sum(header.widths) - NUMBER_SPACE - BAR_COUNT

        for i, title, width, alignment in zip(list(range(len(header.widths))), header.titles, header.widths, header.alignments):
            if width == 0:
                width = flex_width
            if alignment == '<':
                title = title[:width].ljust(width)
            elif alignment == '>':
                title = title[:width].rjust(width)
            elif alignment == '=':
                title = title[:width].center(width)
            else:
                title = title[:width].ljust(width)

            header_row.append(
                U.hi_color(
                    title,
                    background=self.colors['header_bg'],
                    foreground=self.colors['header_fg']
                )
            )
        header_row = title_bar.join(header_row)

        print(header_row)

        # BODY ROWS -----------------------------------------

        # key has the s, r, q, m removed to not interfere with the
        # ask_user options.  This list can have anything, as long as
        # they are single characters.  This is aprox 90 characters.
        key = ('a','b','c','d','e','f','g','h','i','j','k','l','n','o','p',
               't','u','v','w','x','y','z','A','B','C','D','E','F','G','H',
               'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W',
               'X','Y','Z','0','1','2','3','4','5','6','7','8','9','!','"',
               '#','$','%','&',"'",'(',')','*','+',',','-','.','/',':',';',
               '<','=','>','?','@','[','\\',']','^','_','`','{','|','}','~')

        self.table.body = self.table.body[:self.display_count]
        for row, counter in zip(self.table.body, key):
            # look through the title cell to see if any have 720 or 1080 in the
            # string and mark this row as high def if so.
            is_hidef = False
            if '720p' in row[0] or '1080p' in row[0]:
                is_hidef = True

            row_arr = [counter]
            for i, width, align in zip(row, header.widths, header.alignments):
                i = str(i)
                if width == 0:
                    width = flex_width
                row_item = i
                row_item = U.snip(row_item, width)
                row_item = row_item.strip()

                if align == '<':
                    row_item = row_item.ljust(width)
                if align == '>':
                    row_item = row_item.rjust(width)
                if align == '=':
                    row_item = row_item.center(width)
                else:
                    row_item = row_item.ljust(width)

                # if hi def, set the foreground to green
                if is_hidef:
                    row_item = U.hi_color(row_item, foreground=76)

                row_arr.append(row_item)
            print(bar.join(row_arr))

        # USER INPUT ---------------------------------------
        choice = False
        while not choice:
            if self.is_postdownload:
                choice = self.ask_postdownload(key)
            else:
                choice = self.ask(key)
        return choice

    def ask(self, key):
        get = ask_user('\nLetter, [s]kip, skip [r]est of show, [q]uit, [m]ark as watched, or [enter] for #1: ')
        choice = False

        if get == 'q':  # quit
            exit()
        elif get == 's':  # skip
            choice = 'skip'
        elif get == 'r':  # skip rest of series
            choice = 'skip_rest'
        elif get == 'm':  # mark show as watched, but don't download it
            choice = 'mark'
        elif get in key:  # number/letter chosen
            choice_num = key.index(get)
            if choice_num not in list(range(len(self.table.body))):
                self.display_error('Choice not between %s and %s, try again:' % (
                    key[0], key[len(self.table.body) - 1]))
            else:
                choice = self.table.body[choice_num][-1:][0]
        elif get == '[enter]':  # default choice: #1
            choice = self.table.body[0][-1:][0]
        elif get not in key:
            self.display_error('Invalid choice: %s, try again:' % get)

        return choice


    def ask_postdownload(self, key):
        get = ask_user('\nLetter or [q]uit: ')
        choice = False

        if get == 'q':
            exit()
        elif get in key:  # number/letter chosen
            choice_num = key.index(get)
            if choice_num not in list(range(len(self.table.body))):
                self.display_error('Choice not between %s and %s, try again:' % (
                    key[0], key[len(self.table.body) - 1]))
            else:
                choice = self.table.body[choice_num][-1:][0]
        elif get not in key:
            self.display_error('Invalid choice: %s, try again:' % get)

        return choice


    def display_error(self, message):
        print()
        print(U.hi_color('[!]', 16, 178), U.hi_color(message, 178))


if __name__ == '__main__':
    import string
    import random
    from pprint import pprint as pp

    def get_paragraph(min_count, max_count):
        word_count = random.randrange(min_count, max_count)
        paragraph = []
        for i in range(word_count):
            letter_count = random.randrange(1, 10)
            word = random.sample(string.ascii_letters, letter_count)
            word = ''.join(word)
            word = word.replace(' ', '')
            word = word.replace('\t', '')
            paragraph.append(word)
        return ' '.join(paragraph)

    rows = 10
    data = [['This is a title',
             [get_paragraph(1,2), get_paragraph(1,2), get_paragraph(9,10), get_paragraph(9,10), 'RET'],
             [0, 10, 20, 30, 10],
             ['<', '>', '=', '<', '<']],

             [[get_paragraph(1,30),
               get_paragraph(1,30),
               get_paragraph(1,10),
               get_paragraph(1,10),
               get_paragraph(1,2)] for i in range(rows)]
           ]

    for i in range(10):
        tbl2 = ConsoleTable(data)
        tbl2.set_title('New title')
        tbl2.set_count(20)
        out = tbl2.generate()
        print('out:', out)

    data = [['http://thepiratebay.org/search/ Utopia%20S02E03/0/7/0 Utopia%202x03/0/7/0 ',
            ['Name', 'Size', 'Date', 'Seeds'],
            [0, 11, 12, 6],
            ['<', '>', '<', '>']],
           [['Utopia S02E03 HDTV x264-TLA [eztv]',
             '259.23\xa0MiB',
             'Today\xa007:11',
             '2040',
             'magnet:?xt=urn:btih:318938a7a4c8f8b962a90704364138402879a8ad&dn=Utopia+S02E03+HDTV+x264-TLA+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            ['Utopia S02E03 720p HDTV x264-TLA [eztv]',
             '797.83\xa0MiB',
             'Today\xa007:11',
             '881',
             'magnet:?xt=urn:btih:fb185c7c0bd81f8e97481f9c23754ff3e6b5fe15&dn=Utopia+S02E03+720p+HDTV+x264-TLA+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            ['Utopia.S02E03.720p.HDTV.x264-TLA[rartv]',
             '797.83\xa0MiB',
             'Today\xa000:37',
             '527',
             'magnet:?xt=urn:btih:33d01b26f48182f7e681a086e35bdb5132af8d93&dn=Utopia.S02E03.720p.HDTV.x264-TLA%5Brartv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            ['Utopia.S02E03.HDTV.x264-TLA[rartv]',
             '265.27\xa0MiB',
             'Today\xa000:45',
             '230',
             'magnet:?xt=urn:btih:aae14da14213bb2e48963b9c40b5b313056897e7&dn=Utopia.S02E03.HDTV.x264-TLA%5Brartv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            ['Utopia S02E03 480p HDTV x264-mSD ',
             '165.4\xa0MiB',
             'Today\xa001:18',
             '40',
             'magnet:?xt=urn:btih:c454da2eef2f4ed2ffae37fe479c8d99a9c7f5d3&dn=Utopia+S02E03+480p+HDTV+x264-mSD+&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337']]]

    tbl1 = ConsoleTable(data)
    result = tbl1.generate()
    print('result>', result)
