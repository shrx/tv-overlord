#!/usr/bin/env python

import os
import sys
import datetime
from dateutil import parser
from pprint import pprint as pp
import click

from tvoverlord.config import Config
from tvoverlord.db import DB
from tvoverlord.consoletable import ConsoleTable
from tvoverlord.downloadmanager import DownloadManager
from tvoverlord.search import Search
from tvoverlord.util import U
from tvoverlord.tvutil import style


class History:
    def __init__(self, criteria=1):
        self.db = DB()

        if criteria is None:
            criteria = 1

        if isinstance(criteria, int):
            sqldata = self.db.get_downloaded_days(criteria)
        elif isinstance(criteria, datetime.datetime):
            sqldata = self.db.get_downloaded_date(criteria)
        elif isinstance(criteria, str):
            sqldata = self.db.get_downloaded_title(criteria)
        self.sqldata = sqldata

    def episode(self, name, season, episode):
        seep = ''
        if season and episode:
            seep = ' S{0:0>2}E{1:0>2}'.format(season, episode)
        full = name + seep
        return full

    def exists(self, filename):
        if filename is None:
            return ''
        elif os.path.exists(filename):
            filename = filename
        else:
            filename = style(filename, fg='black', strike=True)
        return filename

    def format_date(self, date):
        parsed = parser.parse(date)
        new = parsed.strftime('%a %b/%d')
        return new

    def show(self, what):
        # date, title, season, episode, magnet, oneoff, complete, filename
        if what:
            what = what.replace(' ', '').split(',')
            line = []
            for i in what:
                line.append('{%s}' % i)
            line = '  '.join(line)
        else:
            line = '{date}  {title}  {complete}  {destination}'

        try:
            lengths = [1] * len(self.sqldata[0])
        except IndexError:
            return  # no sql data

        data = []
        lengths = {'date': 1, 'title': 1, 'filename': 1, 'hash': 1,
                   'destination': 1, 'season': 1, 'episode': 1,
                   'magnet': 1, 'oneoff': 1, 'complete': 1, }

        # build list and get the max lengths
        for row in self.sqldata:
            fields = {
                'date': self.format_date(row[0]),
                'title': row[1],
                'filename': self.exists(row[2]),
                'destination': self.exists(row[10]),
                'season': row[4],
                'episode': row[5],
                'magnet': row[6],
                'oneoff': 'one off' if row[7] else 'tracked',
                'complete': 'complete' if row[8] else 'incomplete',
                'hash': row[3],
            }
            data.append(fields)

            for key, value in fields.items():
                new = len(str(value))
                old = lengths[key]
                lengths[key] = max(new, old)

        # pad each field to the data in lengths
        for row in data:
            for name in row:
                try:
                    row[name] = row[name].ljust(lengths[name])
                except AttributeError:
                    # fields has None as value
                    row[name] = ''.ljust(lengths[name])

        for row in data:
            try:
                click.echo(line.format(**row).strip())
            except KeyError:
                sys.exit('Invalid key')

    def copy(self):
        title = 'Copy files to %s' % Config.tv_dir
        selected = self.display_list(title)

        torrent_hash = selected[3]
        torrent_dir, torrent_name = os.path.split(selected[2])

        DownloadManager(torrent_hash, torrent_dir, torrent_name)

    def download(self):
        title = 'Re-download'
        selected = self.display_list(title, download=True)

        url = selected[-1]
        search = Search()
        search.download(chosen_show=url, destination=Config.staging)

    def display_list(self, title, download=False):
        sqldata = self.sqldata
        records = []

        if download:
            data = [
                [
                    title,
                    ['Date downloaded', 'Show name, episode', 'Magnet link'],
                    [16, 25, 0],
                    ['<', '<', '<']
                ]
            ]
            for i in sqldata:
                records.append([
                    self.format_date(i[0]),
                    self.episode(i[1], i[4], i[5]),
                    i[9],
                    i[9]]
                )
        else:
            data = [
                [
                    title,
                    ['Date downloaded', 'Show name, episode', 'Local file'],
                    [16, 25, 0],
                    ['<', '<', '<']
                ]
            ]
            for i in sqldata:
                records.append([
                    self.format_date(i[0]),
                    self.episode(i[1], i[4], i[5]),
                    self.exists(i[2]),
                    i[3]]
                )
        data.append(records)

        tbl = ConsoleTable(data)
        tbl.set_count(None)
        tbl.is_postdownload = True
        torrent_hash = tbl.generate()

        selected = [i for i in data[1] if torrent_hash in i][0]
        return selected


if __name__ == '__main__':
    pass
