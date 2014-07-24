import os
from collections import namedtuple

from ConsoleInput import ask_user
from Util import U


class ConsoleTable:
    def __init__(self, data):
        """Build a table to display data in the terminal

        :param data: An array of arrays.

        data must be in this format:
        [
          # TABLE DESCRIPTION
          [
            'Title string',                        # title string
            ['title', 'title', 'title', 'title'],  # titles of columns
            [10, 5, 0, 20],                        # widths of columns, 0 is flex
            ['<', '>', '=', '>']                   # alignments
          ],

          # TABLE DATA.  Last one is what gets returned
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
        self.return_field = 0
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

    def set_title(self, text):
        self.table.title.text = text

    def set_header(self, header_items):
        self.table.header.titles = header_items

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
        title = U.effects(['boldon'], U.hi_color(
            ('  ' + self.table.title.text).ljust(self.console_columns),
            foreground=self.colors['title_fg'],
            background=self.colors['title_bg'],
        ))
        print title

        # HEADER ROW ---------------------------------------
        header = self.table.header
        header_row = [U.hi_color(' ',     # the number/letter column
                                 background=self.colors['header_bg'],
                                 foreground=self.colors['header_fg'])]
        NUMBER_SPACE = 1
        BAR_COUNT = len(header.widths)
        flex_width = self.console_columns - sum(header.widths) - NUMBER_SPACE - BAR_COUNT

        for i, title, width, alignment in zip(range(len(header.widths)), header.titles, header.widths, header.alignments):
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

        print header_row

        # BODY ROWS -----------------------------------------
        key = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
               'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

        for row, counter in zip(self.table.body, key):
            row_arr = [counter]
            for i, width, align in zip(row, header.widths, header.alignments):
                if width == 0:
                    width = flex_width
                row_item = i
                row_item = U.snip(row_item, width)
                row_item = row_item.strip()
                # row_item = row_item.ljust (width)

                if align == '<':
                    row_item = row_item.ljust(width)
                if align == '>':
                    row_item = row_item.rjust(width)
                if align == '=':
                    row_item = row_item.center(width)
                else:
                    row_item = row_item.ljust(width)

                row_arr.append(row_item)
            print bar.join(row_arr)

        # USER INPUT ---------------------------------------
        choice = ''
        get = ask_user('\nNumber, [s]kip, skip [r]est of show, [q]uit or [enter] for #1: ')

        if get == 'q':  # quit
            exit()
        elif get == 's':  # skip
            return
        elif get == 'r':  # skip rest of series
            skip_rest = True
            return 'skip_rest'
        elif get in key:  # number/letter chosen
            choice_num = [i for i, j in enumerate(key) if j == get][0]
            choice = int(choice_num)
            if choice not in range(len(self.table.body)):
                U.wr('Number not between 1 and %s, try again' % (len(self.table.body)))
                self.generate()
                return
        elif get == '[enter]':  # default choice: #1
            choice = 0
        else:
            print 'Wrong choice, %s' % get
            self.generate()
            return

        return self.table.body[choice][-1:]


if __name__ == '__main__':
    import string
    import random
    from pprint import pprint as pp

    def get_paragraph(min_count, max_count):
        word_count = random.randrange(min_count, max_count)
        paragraph = []
        for i in range(word_count):
            letter_count = random.randrange(1, 10)
            word = random.sample(string.letters, letter_count)
            word = ''.join(word)
            word = word.replace(' ', '')
            word = word.replace('\t', '')
            paragraph.append(word)
        return ' '.join(paragraph)

    data_body = []
    for i in range(12):
        data_body.append([get_paragraph(1,30), get_paragraph(1,30), get_paragraph(1,10), get_paragraph(1,10), get_paragraph(1,2)])

    data = [['This is a title',
             [get_paragraph(1,2), get_paragraph(1,2), get_paragraph(9,10), get_paragraph(9,10)],
             [0, 10, 20, 30],
             ['<', '>', '=', '<']],
             data_body
        ]

    tbl2 = ConsoleTable(data)
    tbl2.set_title('New title')
    print tbl2.generate()

    data = [['http://thepiratebay.org/search/ Utopia%20S02E03/0/7/0 Utopia%202x03/0/7/0 ',
            ['Name', 'Size', 'Date', 'Seeds'],
            [0, 11, 12, 6],
            ['<', '>', '<', '>']],
           [[u'Utopia S02E03 HDTV x264-TLA [eztv]',
             u'259.23\xa0MiB',
             u'Today\xa007:11',
             u'2040',
             'magnet:?xt=urn:btih:318938a7a4c8f8b962a90704364138402879a8ad&dn=Utopia+S02E03+HDTV+x264-TLA+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            [u'Utopia S02E03 720p HDTV x264-TLA [eztv]',
             u'797.83\xa0MiB',
             u'Today\xa007:11',
             u'881',
             'magnet:?xt=urn:btih:fb185c7c0bd81f8e97481f9c23754ff3e6b5fe15&dn=Utopia+S02E03+720p+HDTV+x264-TLA+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            [u'Utopia.S02E03.720p.HDTV.x264-TLA[rartv]',
             u'797.83\xa0MiB',
             u'Today\xa000:37',
             u'527',
             'magnet:?xt=urn:btih:33d01b26f48182f7e681a086e35bdb5132af8d93&dn=Utopia.S02E03.720p.HDTV.x264-TLA%5Brartv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            [u'Utopia.S02E03.HDTV.x264-TLA[rartv]',
             u'265.27\xa0MiB',
             u'Today\xa000:45',
             u'230',
             'magnet:?xt=urn:btih:aae14da14213bb2e48963b9c40b5b313056897e7&dn=Utopia.S02E03.HDTV.x264-TLA%5Brartv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337'],
            [u'Utopia S02E03 480p HDTV x264-mSD ',
             u'165.4\xa0MiB',
             u'Today\xa001:18',
             u'40',
             'magnet:?xt=urn:btih:c454da2eef2f4ed2ffae37fe479c8d99a9c7f5d3&dn=Utopia+S02E03+480p+HDTV+x264-mSD+&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Fopen.demonii.com%3A1337']]]

    tbl1 = ConsoleTable(data)
    result = tbl1.generate()
    print 'result>', result
