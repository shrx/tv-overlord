#!/usr/bin/env python
import os
import sys


def dict_factory(cursor, row):
    """Changes the data returned from the db from a
    tupple to a dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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


if __name__ == '__main__':

    pass
