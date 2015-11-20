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
            print(msg)
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


if __name__ == '__main__':

    pass
