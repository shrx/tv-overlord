#!/usr/bin/env python
import os
import sys
import textwrap
import re
from pprint import pprint as pp
from collections import namedtuple


def dict_factory(cursor, row):
    """Changes the data returned from the db from a
    tupple to a dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def format_paragraphs(msg):
    paragraphs = re.split('\n\n+', msg)
    for i, paragraph in enumerate(paragraphs):
        paragraph = textwrap.dedent(paragraph).strip()
        paragraph = textwrap.fill(paragraph)
        paragraphs[i] = paragraph
    document = '\n\n'.join(paragraphs)
    return document


class FancyPrint:
    def __init__(self):
        console_rows, console_columns = os.popen('stty size', 'r').read().split()
        self.bs = '\b' * int(console_columns)
        self.console_columns = int(console_columns)

    def standard_print(self, msg):
        msg = '\n'.join([i.ljust(self.console_columns) for i in msg.split('\n')])
        msg = msg + '\n'
        self._back_print(msg)

    def done(self, msg=''):
        msg = msg.ljust(self.console_columns)
        sys.stdout.write('\033[F')
        self._back_print(msg)

    def _back_print(self, msg):
        full_msg = '%s%s' % (self.bs, msg)

        sys.stdout.write(full_msg)
        sys.stdout.flush()


# http://stackoverflow.com/a/6397492
def disk_info(path):
    """Return disk usage associated with path."""
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    usage_ntuple = namedtuple('usage',  'total used free percent')
    return usage_ntuple(total, used, free, round(percent, 1))


if __name__ == '__main__':
    pass
