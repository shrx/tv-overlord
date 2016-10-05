
"""
Build a table to display data in a terminal.
"""

import sys
import re
from collections import namedtuple
from pprint import pprint as pp
import click

from tvoverlord.config import Config
from tvoverlord.util import U
from tvoverlord.tvutil import style


class ConsoleTable:
    def __init__(self, data, table_type, nondb=False):
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
        if table_type not in ['download', 'nondb', 'copy', 'redownload']:
            sys.exit('invalid table_type: "%s"' % table_type)
        self.table_type = table_type

        # self.nondb = True if nondb else False
        self.display_count = 5
        # self.is_postdownload = False

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

    def generate(self):
        colors = Config.color.table
        title_bar = style(
            '|',
            fg=colors.bar.fg,
            bg=colors.header.bg,)
        bar = style(
            '|',
            fg=colors.bar.fg,
        )

        # TITLE --------------------------------------------
        title = '  %s' % self.table.title.text
        title = title.ljust(Config.console_columns)
        title = style(title,
                      bold=True,
                      fg=colors.title.fg,
                      bg=colors.title.bg)
        click.echo(title)

        # HEADER ROW ---------------------------------------
        header = self.table.header
        header_row = [style(' ', bg=colors.header.bg,
                                 fg=colors.header.fg)]
        NUMBER_SPACE = 1
        BAR_COUNT = len(header.widths)
        flex_width = (Config.console_columns - sum(header.widths) -
                      NUMBER_SPACE - BAR_COUNT)

        for title, width, alignment in zip(header.titles,
                                           header.widths,
                                           header.alignments):
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
                style(title,
                      bg=colors.header.bg,
                      fg=colors.header.fg,
                )
            )

        header_row = title_bar.join(header_row)

        click.echo(header_row)

        # BODY ROWS -----------------------------------------

        key = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVW"""
        key += """XYZ0123456789!#$%&()*+-./:;<=>?@[\\]^_`|}{"'~"""
        if self.table_type == 'download':
            options = '\nLetter, [s]kip, skip [r]est of show, [q]uit or [m]ark as downloaded: '
            key = re.sub('[srqm]', '', key)

        elif self.table_type == 'nondb':
            options = '\nLetter or [q]uit: '
            key = re.sub('[q]', '', key)

        elif self.table_type == 'copy':
            options = '\nLetter, [a]ll or [q]uit: '
            key = re.sub('[aq]', '', key)

        elif self.table_type == 'redownload':
            options = '\nLetter or [q]uit: '
            key = re.sub('[q]', '', key)


        self.table.body = self.table.body[:self.display_count]
        for row, counter in zip(self.table.body, key):
            # look through the title cell to see if any have 720 or
            # 1080 in the string and mark this row as high def.
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
                    row_item = style(row_item, fg=colors.hidef.fg)

                row_arr.append(row_item)
            click.echo(bar.join(row_arr))

        # USER INPUT ---------------------------------------
        choice = False
        while not choice:
            choice = self.ask(options, key)
        return choice

    def ask(self, options, key):
        click.echo(options, nl=False)
        get = click.getchar()
        # On Windows, getchar returns a byte string which looks like a bug
        # https://github.com/pallets/click/issues/537
        if Config.is_win:
            try:
                get = get.decode('utf-8')
            except UnicodeDecodeError:
                # On windows, if a non character key (like an arrow
                # key) is pressed, there looks like there are two key
                # press events which causes a second loop through this
                # function.  In the case of a right arrow key, the
                # second key is an 'M' which would cause an
                # inadvertent selection if there was an 'M' option.
                # The non char key causes a UnicodeDecodeError so
                # we'll stop here.
                sys.exit('Invalid key')

        click.echo(get)
        choice = False

        key = list(key)

        if self.table_type == 'download':
            if get == 'q':    # quit
                sys.exit()
            elif get == 's':  # skip
                choice = 'skip'
            elif get == 'r':  # skip rest of series
                choice = 'skip_rest'
            elif get == 'm':  # mark show as watched, but don't download it
                choice = 'mark'

        elif self.table_type == 'copy':
            if get == 'q':
                sys.exit()
            elif get == 'a':
                choice = 'copy_all'

        elif self.table_type in ['redownload', 'nondb']:
            if get == 'q':
                sys.exit()

        if get in key:  # number/letter chosen
            choice_num = key.index(get)
            if choice_num not in list(range(len(self.table.body))):
                self.display_error('Choice not between %s and %s, try again:' % (
                    key[0], key[len(self.table.body) - 1]))
            else:
                choice = self.table.body[choice_num][-1:][0]
        elif not choice and get not in key:
            self.display_error('Invalid choice, try again:')

        return choice

    def display_error(self, message):
        colors = Config.color
        click.echo()
        click.echo('%s %s' % (
            style('[!]',
                  fg=colors.warn.fg,
                  bg=colors.warn.bg),
            style(message,
                  fg=colors.warn.fg))
        )


if __name__ == '__main__':
    pass
