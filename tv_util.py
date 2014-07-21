#!/usr/bin/env python

import os
import sys
import urllib2
import json

from Util import U
from ConsoleInput import ask_user
from tv_config import Config


class FancyPrint:
    def __init__(self):
        self.prev_fancy = False
        console_rows, console_columns = os.popen('stty size', 'r').read().split()
        self.bs = '\b' * int(console_columns)
        self.console_columns = int(console_columns)


    def standard_print(self, msg):
        msg = '\n'.join([i.ljust(self.console_columns) for i in msg.split('\n')])
        if self.prev_fancy:
            msg += '\n'
            self._back_print(msg)
        else:
            print msg
        self.prev_fancy = False


    def fancy_print(self, msg):
        msg = msg.ljust(self.console_columns)
        if self.prev_fancy:
            self._back_print(msg)
        else:
            sys.stdout.write(msg)
            sys.stdout.flush()
        self.prev_fancy = True


    def done(self, msg=''):
        msg = msg.ljust(self.console_columns)
        self._back_print(msg)


    def _back_print(self, msg):
        full_msg = '%s%s' % (self.bs, msg)

        sys.stdout.write(full_msg)
        sys.stdout.flush()


class Ask:
    def __init__(self):
        self.title = False
        self.header = []
        self.rows = []
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
            'bar': 19, }


    def set_title(self, text):
        self.title = text


    # header_items = [{'text':text, 'width':width, 'justification':justification}, ...]
    def set_header(self, header_items):
        for i in header_items:
            self.header.append(i)


    def set_return_field(self, field):
        self.return_field = field - 1


    def header_item(self, text, width=10, align='left', ret_field=False):
        self.header.append({
            'text': text,
            'width': width,
            'justification': align,
            'ret_field': ret_field,
        })


    def set_row(self, row):
        self.rows.append(row)


    def ask(self):
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
        if self.title:
            title = U.effects(['boldon'], U.hi_color(
                ('  ' + self.title).ljust(self.console_columns),
                foreground=self.colors['title_fg'],
                background=self.colors['title_bg'],
            ))
            print title

        # HEADER ROW ---------------------------------------
        header = []
        widths = []
        alignment = []

        non_flex = 0
        for i in self.header:
            widths.append(i['width'])  # make a widths array so they can be used later in the body
            non_flex += int(i['width'])
            alignment.append(i['justification'])

        # number/letter column
        header.append(
            U.hi_color(
                ' ',
                background=self.colors['header_bg'],
                foreground=self.colors['header_fg'], ))

        NUMBER_SPACE = 2
        BAR_COUNT = len(self.header)

        for i in self.header:
            width = i['width']
            if width == 0:  # flex column
                width = self.console_columns - non_flex - NUMBER_SPACE - BAR_COUNT
                flex_width = width

            header_title = U.snip(i['text'], width)
            header_title = header_title.ljust(width)

            # if i['justification'] == 'left':
            # header_title = i['text'].ljust (width)
            # else:
            # header_title = i['text'].rjust (width)

            header.append(
                U.hi_color(
                    header_title,
                    background=self.colors['header_bg'],
                    foreground=self.colors['header_fg'], ))

        header_row = title_bar.join(header)
        print header_row

        # BODY ROWS -----------------------------------------
        key = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
               'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

        for row, counter in zip(self.rows, key):
            row_arr = [counter]
            for i, width, align in zip(row, widths, alignment):
                if width == 0:
                    width = flex_width
                row_item = i
                row_item = U.snip(row_item, width)
                row_item = row_item.strip()
                # row_item = row_item.ljust (width)

                if align == 'left':
                    row_item = row_item.ljust(width)
                else:
                    row_item = row_item.rjust(width)

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
            if choice not in range(len(self.rows)):
                U.wr('Number not between 1 and %s, try again' % (len(self.rows)))
                self.ask()
                return
        elif get == '[enter]':  # default choice: #1
            choice = 0
        else:
            print 'Wrong choice, %s' % get
            self.ask()
            return

        # pos = 0
        # for i, j in zip (self.header, range (len (self.header))):
        # if i['ret_field']:
        # print j, i['ret_field']
        # pos = j

        return self.rows[choice][self.return_field]


class RT:
    def __init__(self):
        self.api_key = Config.rt_apikey


    def search(self, title):
        url = 'api.rottentomatoes.com/api/public/v1.0/movies.json\
            ?q={title}&page_limit=50&page=1&apikey={key}'
        url = url.format(title=title, key=self.api_key)
        return self._get_data(url)


    def details(self, rt_id):
        url = 'api.rottentomatoes.com/api/public/v1.0/movies/{rt_id}.json\
            ?apikey={key}&_prettyprint=false'
        url = url.format(rt_id=rt_id, key=self.api_key)
        return self._get_data(url)


    def imdb_details(self, imdb_id):
        url = 'http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?type=imdb&id={imdb_id}&apikey={key}&_prettyprint=false'
        url = url.format(imdb_id=imdb_id, key=self.api_key)
        return self._get_data(url)


    def _get_data(self, url):
        header = {'User-Agent': 'Mozilla/5.0 (X11;U; Linux i686; en-GB; rv:1.9.1) \
            Gecko/20090624 Ubuntu/9.04 (jaunty) Firefox/3.5'}
        request = urllib2.Request(url=url)

        # print url
        # response = urllib2.urlopen (request)
        # page = response.read()
        # print page

        try:
            response = urllib2.urlopen(request)
            page = response.read()
        except Exception:
            U.wr('ERROR: httplib.BadStatusLine')
            page = ''

        data = json.loads(page)
        return data


if __name__ == '__main__':

    import string
    import random

    def get_paragraph():
        word_count = random.randrange(1, 10)
        paragraph = []
        for i in range(word_count):
            letter_count = random.randrange(1, 10)
            # word = random.sample (string.printable, letter_count)
            word = random.sample(string.letters, letter_count)
            word = ''.join(word)
            word = word.replace(' ', '')
            word = word.replace('\t', '')
            paragraph.append(word)
        return ' '.join(paragraph)


    # print get_paragraph()
    # print get_paragraph()
    # print get_paragraph()
    # exit()

    tbl = Ask()
    tbl.set_title('This is the title')

    tbl.header_item(text='dog', width=20)
    tbl.header_item(text='cat', width=0)
    tbl.header_item(text='horse', width=20)
    tbl.header_item(text='water buffalo', width=20)

    tbl.set_return_field(4)

    for i in range(5):  # row count
        body = []
        for j in range(5):  # column count
            para = get_paragraph()
            body.append(para)

        tbl.set_row(body)
    tbl.ask()

    # designate 1 column as the flex width
    # add number/letter col at start
    # return return value



    # import time
    #
    # l = ('dog', 'cat', 'cow', 'horse', 'pig', 'water buffalo')
    # fp = FancyPrint()
    # for i, counter in zip (l, range (len (l))):
    # time.sleep (1)
    # if counter == 2:
    # fp.standard_print (i)
    # else:
    # fp.fancy_print ('Current animal: %s' % i)
