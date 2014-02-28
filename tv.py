#!/usr/bin/python

r'''
Usage:
  tv download    [-n] [-d DB-FILE] [-l LOCATION] [-p PROVIDER]
  tv showmissing [-n] [-d DB-FILE]
  tv info        [-n] [-d DB-FILE] [-a] [-x] [--ask-inactive] [--show-links]
  tv calender    [-n] [-d DB-FILE] [-a] [-x] [--no-color] [--width WIDTH]
  tv addnew SHOW_NAME [-d DB-FILE]
  tv nondbshow SEARCH_STRING [-l LOCATION] [-p PROVIDER]
  tv editdbinfo SHOW_NAME [-d DB-FILE]
  tv providers

Options:
  -h, --help
  -d DB-FILE, --db-file DB-FILE
                    The db file to use instead of the default one which is
                    specified in config.ini
  -l DOWNLOAD_LOCATION, --location DOWNLOAD_LOCATION
                    Location to download the nzb files to
  -n, --no-cache    Re-download the show data instead of using the cached data
  -p SEARCH_PROVIDER, --search-provider SEARCH_PROVIDER
                    Specify a different search engine instead of the one
                    in the config file.
  -a, --show-all    Show all shows including the ones marked inactive
  -x, --sort-by-next  Sort by release date instead of the default alphabetical
  --ask-inactive    Ask to make inactive shows that are cancelled
  --show-links      Show links to IMDB.com and TheTVDb.com for each show
  --width WIDTH     The width of the calendar in characters
  --no-color        Don't use color in output, useful if output is to be
                    used in email or text file.
'''

import StringIO
import datetime
from dateutil import parser as dateParser
import gzip
import os
import re
import sqlite3
import time
from docopt import docopt
import tvdb_api
import pprint
import textwrap

import sys
from ConsoleInput import ask_user as ask
import Search
from tv_config import config
from tv_util import FancyPrint
from Util import U


def se_ep (season, episode):
    season_just = str (season).rjust (2, '0')
    episode = str (episode).rjust (2, '0')
    fixed = 'S%sE%s' % (season_just, episode)

    return fixed


class Series:
    '''
    Local db fields added:
    ----------------------
    db_current_season, db_last_episode, db_name, db_thetvdb_series_id

    Thetvdb season fields added:
    ----------------------------
    actors, added, addedby, airs_dayofweek, airs_time, banner,
    contentrating, fanart, firstaired, genre, get_thetvdb_data, id,
    imdb_id, language, lastupdated, network, networkid, overview,
    poster, rating, ratingcount, runtime, seriesid, seriesname,
    set_db_data, status, zap2it_id

    Thetvdb episode fieldnames:
    ---------------------------
    episodenumber, rating, overview, dvd_episodenumber, dvd_discid,
    combined_episodenumber, epimgflag, id, seasonid, seasonnumber,
    writer, lastupdated, filename, absolute_number, ratingcount,
    combined_season, imdb_id, director, dvd_chapter, dvd_season,
    gueststars, seriesid, language, productioncode, firstaired,
    episodename
    '''

    def __init__ (self, provider, dbdata=[], show_type='current'):
        typelist = ('new', 'nondb', 'current')
        if show_type not in typelist:
            raise exception ('incorrect show type')
        if show_type == 'current':
            self._set_db_data (dbdata)
            self._get_thetvdb_series_data()
            self.search_provider = Search.Search(provider)

        if show_type == 'nondb':
            self.search_provider = Search.Search(provider)

        self.console_rows, self.console_columns = os.popen ('stty size', 'r').read().split()


    def _set_db_data (self, dbdata):
        '''Add the data from the local db'''
        self.db_name = dbdata['name']
        self.db_thetvdb_series_id = dbdata['thetvdb_series_id']
        self.db_ragetv_series_id = dbdata['ragetv_series_id']
        self.db_current_season = dbdata['season']
        self.db_last_episode = dbdata['episode']
        # Sometimes the thetvdb name is slighly different than the
        # name to use for searching, thats why we use search_engine_name
        self.db_search_engine_name = dbdata['search_engine_name']
        self.db_status = dbdata['status']


    def _get_thetvdb_series_data (self):
        '''Dynamicaly add all the data from Thetvdb.com

        networkid      - None
        rating         - 8.6
        airs_dayofweek - Thursday
        contentrating  - TV-14
        seriesname     - 30 Rock
        id             - 79488
        airs_time      - 8:30 PM
        network        - NBC
        fanart         - http://www.thetvdb.com/banners/fanart/original/79488-11.jpg
        lastupdated    - 1358045748
        actors         - |Tina Fey|Alec Baldwin|Tracy Morgan|Jane Krakowski|Kevin Brown|Maulik Pancholy|Keith Powell|Katrina Bowden|Lonny Ross|Scott Adsit|Judah Friedlander|Jack McBrayer|John Lutz|Grizz Chapman|
        ratingcount    - 196
        status         - Continuing
        added          - None
        poster         - http://www.thetvdb.com/banners/posters/79488-7.jpg
        imdb_id        - tt0496424
        genre          - |Comedy|
        banner         - http://www.thetvdb.com/banners/graphical/79488-g11.jpg
        seriesid       - 58326
        language       - en
        zap2it_id      - SH00848357
        addedby        - None
        firstaired     - 2006-10-11
        runtime        - 30
        overview       - Emmy Award Winner Tina Fey writ...

        '''

        tv = tvdb_api.Tvdb (apikey=config.thetvdb_apikey, cache=config.use_cache)
        try:
            series = tv[self.db_name]
        except tvdb_api.tvdb_shownotfound:
            print 'Show not found: %s' % (self.db_name)
            return
        except tvdb_api.tvdb_error as e_msg:
            print '\n'
            print 'Error: %s' % (self.db_name)
            print '-----------------------------'
            print e_msg
            return

        for i in series.data:
            setattr (self, i, series.data[i])
        self.series = series


    def download_missing (self):
        missing = self._get_missing()
        if self.db_search_engine_name:
            search_title = self.db_search_engine_name
        else:
            search_title = self.db_name

        # if self does not have the attirbute series
        # its because of an error in the xml downloaded
        # from thetvdb site
        if not hasattr (self, 'series'):
            return

        for episode in missing:
            showid = None

            showlist = []
            error_a = error_b = False
            try:
                results = self.search_provider.search(
                        search_title,
                        season=episode['season'],
                        episode=episode['episode'],
                        )

            except Search.SearchError as inst:
                    error_a = True

            if results:
                showid = self._ask (
                    results,
                    season=episode['season'],
                    episode=episode['episode'])
            else:
                print '"%s" is listed in TheTVDB, but not found at the search engine' % (
                    search_title)

            if showid == 'skip_rest':
                return

            if showid == 'mark':
                # mark the episode as watched, but don't download it
                self._update_db (season=episode['season'], episode=episode['episode'])
                continue

            if not showid:
                continue

            self._download (showid)
            self._update_db (season=episode['season'], episode=episode['episode'])


    def is_missing (self):
        missing = self._get_missing()
        self.missing = missing

        ret = True
        try:
            if len (missing) == 0:
                ret = False
        except:
            ret = False

        return ret


    def show_missing (self):
        missing = self.missing
        if len (missing) == 0:
            return False
        ret = '%s' % (U.effects (['boldon', 'greenf'], self.db_name))
        ret += '\n'
        indent = '    '
        missing_list = []
        for s in missing:
            se = 'S%sE%s' % (s['season'].rjust(2, '0'), s['episode'].rjust(2, '0'))
            missing_list.append (se)
        ret += textwrap.fill (', '.join (missing_list), width=int(self.console_columns),
                              initial_indent=indent, subsequent_indent=indent)
        return ret


    def add_new (self, name):
        self.db_name = name
        self._get_thetvdb_series_data()
        indent = '  '

        print
        print self.seriesname
        print '-' * len (self.seriesname)
        print textwrap.fill (self.overview, width=int (self.console_columns),
                             initial_indent=indent, subsequent_indent=indent)
        print
        print '%sFirst aired: %s' % (indent, self.firstaired)
        print '%sStatus: %s' % (indent, self.status)
        print

        correct = ask ('Is this the correct show? [y/n]')

        if correct == 'y':
            self._add_new_db()


    def non_db (self, search_str):
        self.db_name = search_str
        try:
            show_data = self._ask(self.search_provider.search(search_str), None, None)
            if not show_data: return
        except Search.SearchError:
            print 'No matches'
            return
        self._download (show_data)


    def _get_missing (self):
        '''Returns a list of missing episodes'''
        missing = []
        today = datetime.date.today()
        last_watched = se_ep (self.db_current_season, self.db_last_episode)

        # if SELF does not have the attribute: 'series'
        # it's because of an error in the xml downloaded
        # from thetvdb site
        if not hasattr (self, 'series'):
            return

        for i in self.series:           # for each season
            for j in self.series[i]:    # for each episode
                b_date = self.series[i][j]['firstaired']
                if not b_date: continue  # some episode have no broacast date?
                split_date = b_date.split ('-')
                broadcast_date = datetime.date (
                    int (split_date[0]), int (split_date[1]), int (split_date[2]))
                if broadcast_date >= today:  # unaired future date
                    break

                last_season = self.series[i][j]['seasonnumber']
                last_episode = self.series[i][j]['episodenumber']
                last_broadcast = se_ep (last_season, last_episode)
                if (last_watched < last_broadcast):
                    missing.append ({'season':last_season, 'episode':last_episode})

        return missing


    def _ask (self, shows, season, episode):
        class color:
            title_bg = 19
            title_fg = None
            tb_header_fg = None #39
            tb_header_bg = 17
            tb_body_fg = 'white'
            tb_body_bg = None
            bar = title_bg

        title_bar = U.hi_color ('|', foreground=color.bar, background=color.tb_header_bg)
        bar =       U.hi_color ('|', foreground=color.bar)

        ### Title bar row ###
        print
        if season and episode:
            show_title = '%s %s' % (self.db_name, se_ep (season, episode))
        else:
            show_title = self.db_name

        print U.effects (['boldon'], U.hi_color (
            show_title.ljust (int (self.console_columns)),
            foreground=color.title_fg,
            background=color.title_bg,
            ))

        ### Header row ###
        num_w = 1
        header_titles = [' '] + shows[0][1]
        all_length = num_w + sum(shows[0][2]) + 4 # width of first column: 1...Z
        title_w = int (self.console_columns) - all_length
        header_widths = [num_w] + [title_w if x is 0 else x for x in shows[0][2]]
        head_row = []
        for header_title, header_width in zip(header_titles, header_widths):
            head_row.append(
                U.hi_color(header_title.ljust (header_width),
                           background=color.tb_header_bg))
        print title_bar.join(head_row)

        ### Matched episodes ###
        alignments = ['>'] + shows[0][3]
        key = ('1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i',
               'j','k','l','n','o','p','q','r','s','t','u','v','w','x','y','z')
        for row, counter in zip (shows[1], key):
            full_row = [counter] + row
            for width, i, alignment in zip (header_widths,
                                            range(len(header_widths)),
                                            alignments):
                text = full_row[i]
                if len(text) >= width:
                    text = U.snip(text, width)

                if alignment == '<':
                    full_row[i] = text.ljust(width)
                elif alignment == '>':
                    full_row[i] = text.rjust(width)
                elif alignment == '=':
                    full_row[i] = text.center(width)
                else:
                    full_row[i] = text.ljust(width)
            print bar.join(full_row[:-1])

        # User Input
        choice = ''
        get = ask ('\nNumber, [s]kip, skip [r]est of show, [q]uit, [m]ark as watched, or [enter] for #1.\nChoice: ')

        if get == 'q':      # quit
            exit()
        elif get == 's':    # skip
            return
        elif get == 'r':    # skip rest of series
            skip_rest = True
            return 'skip_rest'
        elif get in key:    # number choice
            choice_num = [i for i,j in enumerate (key) if j == get][0]
            choice = int (choice_num)
            if choice not in range (len (shows[1])):
                U.wr ('Number not between 1 and %s' % (len (shows[1])))
                return
        elif get == 'm':    # mark show as watched, but don't download it
            return 'mark'
        elif get == '[enter]':  # default #1
            choice = 0
        else:
            print 'Wrong choice'
            return

        return shows[1][choice][-1:][0]


    def _download (self, show_data):
        msg = U.hi_color ('Downloading...', foreground=16, background=184)
        sys.stdout.write (msg)
        sys.stdout.flush()

        filename = self.search_provider.download(chosen_show=show_data, destination=config.staging)

        backspace = '\b' * len (msg)
        done = U.hi_color (filename.ljust (len (msg)), foreground=34)
        print '%s%s' % (backspace, done)


    def set_inactive (self):
        sql = 'UPDATE shows SET status="inactive" WHERE thetvdb_series_id=:tvdb_id'
        conn = sqlite3.connect (config.db_file)
        curs = conn.cursor()
        values = {'tvdb_id':self.db_thetvdb_series_id}
        curs.execute (sql, values)

        conn.commit()
        conn.close()


    def _update_db (self, season, episode):
        sql = "UPDATE shows SET season=:season, episode=:episode WHERE thetvdb_series_id=:tvdb_id"
        conn = sqlite3.connect (config.db_file)
        curs = conn.cursor()
        values = {'season':season, 'episode':episode, 'tvdb_id':self.db_thetvdb_series_id}
        curs.execute (sql, values)

        conn.commit()
        conn.close()


    def _add_new_db (self, season=0, episode=0):
        sql = '''insert into shows (
            network_status, status, thetvdb_series_id, name, season, episode)
            values (:network_status, :status, :thetvdb_id, :name, :season, :episode)'''
        values = {'network_status': self.status,
                  'status': 'active',
                  'thetvdb_id': self.seriesid,
                  'name': self.seriesname,
                  'season': season,
                  'episode': episode}
        print values
        conn = sqlite3.connect (config.db_file)
        curs = conn.cursor()
        curs.execute (sql, values)
        conn.commit()
        conn.close()


class AllSeries:
    '''Return an iterable class of Series'''
    def __init__ (self, provider):
        self.dbdata = self._query_db()
        self.index = len (self.dbdata)
        self.i = 0
        self.provider = provider
    def __iter__ (self):
        return self
    def next (self):
        if self.i == len (self.dbdata):
            raise StopIteration
        series = Series (self.provider, dbdata=self.dbdata[self.i])
        self.i = self.i + 1
        return series

    def _query_db (self):
        sql = "SELECT name, season, episode, thetvdb_series_id, \
            ragetv_series_id, search_engine_name, status \
            FROM shows WHERE status='active' ORDER BY replace (name, 'The ', '');"
        conn = sqlite3.connect (config.db_file)
        conn.row_factory = dict_factory
        curs = conn.cursor()
        ddata = curs.execute (sql)
        data = []
        for i in ddata:
            data.append (i)
        conn.commit()
        conn.close()
        return data


def dict_factory (cursor, row):
    '''Changes the data returned from the db from a
    tupple to a dictionary'''
    d = {}
    for idx, col in enumerate (cursor.description):
        d[col[0]] = row[idx]
    return d


def edit_db (search_str):
    sql = 'SELECT * FROM shows WHERE name=:search'
    conn = sqlite3.connect (config.db_file)
    conn.row_factory = dict_factory
    curs = conn.cursor()
    values = {'search': search_str}
    curs.execute (sql, values)
    row = curs.fetchone()

    if not row:
        print '"%s" not found' % search_str
        exit()

    is_error = False

    print 'While editing a field, hit <enter> to leave it unchanged.'
    print 'Type "<ctrl> c" to cancel all edits.\n'
    try:
        new_name = raw_input ('Name: (%s) ' % (row['name']))
        if not new_name:
            new_name = row['name']

        new_search_engine_name = raw_input ('Search engine title: (%s) ' % (row['search_engine_name']))
        if not new_search_engine_name:
            new_search_engine_name = row['search_engine_name']

        new_season = raw_input ('Current season: (%s) ' % (row['season']))
        if not new_season:
            new_season = str(row['season'])

        new_episode = raw_input ('Last episode: (%s) ' % (row['episode']))
        if not new_episode:
            new_episode = str(row['episode'])

        new_status = raw_input ('Status: (%s) ' % (row['status']))
        if not new_status:
            new_status = row['status']

        print

    except KeyboardInterrupt:
        print '\nDatabase edit canceled.'
        exit()

    if not new_season.isdigit():
        print 'Error: Season must be a number'
        is_error = True

    if not new_episode.isdigit():
        print 'Error: Episode must be a number'
        is_error = True

    if new_status not in ['active', 'inactive']:
        print 'Error: Status must be either "active" or "inactive"'
        is_error = True

    if is_error:
        exit()

    sql = '''UPDATE shows SET name=:name, season=:season,
        episode=:episode, status=:status, search_engine_name=:search_engine_name
        WHERE thetvdb_series_id=:tvdb_id'''

    row_values = {'name':new_name, 'season':new_season, 'episode':new_episode,
                  'status':new_status, 'search_engine_name':new_search_engine_name,
                  'tvdb_id':row['thetvdb_series_id']}

    curs.execute (sql, row_values)

    print 'Database updated'

    conn.commit()
    conn.close()


def init (args):

    if args['--db-file']:
        config.db_file = args['--db-file']
    if args['--location']:
        config.staging = args['--location']
    if args['--no-cache']:
        config.use_cache = False

    if args['--search-provider']:
        provider = args['--search-provider']
    else:
        provider = config.providers[0]

    if args['info']:
        show_info = {}
        counter = 0
        for series in AllSeries(provider):
            title = series.db_name

            # check if the series object has a status attribute. if it
            # doesn't then its probably a show that nothing is known
            # about it yet.
            if 'status' not in dir(series):
                continue

            if series.status == 'Ended':
                status = U.hi_color (series.status, foreground=196)
            else:
                status = ''

            # build first row of info for each show
            se = 'Last downloaded: S%sE%s' % (
                str (series.db_current_season).rjust (2, '0'),
                str (series.db_last_episode).rjust (2,'0'),
                )
            se = U.hi_color(se, foreground=48)

            if args['--show-links']:
                imdb_url = U.hi_color(   '\n    IMDB.com:    http://imdb.com/title/%s' % series.imdb_id, foreground=20)
                thetvdb_url = U.hi_color('\n    TheTVDB.com: http://thetvdb.com/?tab=series&id=%s' % series.id, foreground=20)
            else:
                imdb_url = ''
                thetvdb_url = ''

            first_row_a = []
            for i in [title + ',', se, status, imdb_url, thetvdb_url]:
                if i: first_row_a.append(i)
            first_row = ' '.join(first_row_a)

            # build 'upcoming episodes' list
            today = datetime.datetime.today()
            first_time = True
            episodes_list = []
            counter += 1
            next_episode_days = 0
            for i in series.series: # season
                for j in series.series[i]: # episode
                    b_date = series.series[i][j]['firstaired']
                    if not b_date: continue  # some episode have no broadcast date?
                    split_date = b_date.split ('-')
                    broadcast_date = datetime.datetime (
                        int (split_date[0]), int (split_date[1]), int (split_date[2]))

                    if not args['--show-all']:
                        if broadcast_date < today:
                            continue

                    future_date = dateParser.parse (b_date)
                    diff = future_date - today
                    fancy_date = future_date.strftime ('%b %-d')
                    if broadcast_date >= today:
                        episodes_list.append ('S%sE%s, %s (%s)' % (
                            series.series[i][j]['seasonnumber'].rjust (2, '0'),
                            series.series[i][j]['episodenumber'].rjust (2, '0'),
                            fancy_date,
                            diff.days + 1,
                        ))

                    if first_time:
                        first_time = False
                        if args['--sort-by-next']:
                            sort_key = str(diff.days).rjust(5, '0') + str(counter)
                        else:
                            sort_key = series.db_name.replace('The ', '')

            if not first_time:
                if episodes_list:
                    indent = '    '
                    episode_list = 'Future episodes: ' + ' - '.join (episodes_list)
                    episodes = textwrap.fill (
                        U.hi_color (episode_list, foreground=22),
                        width=int(series.console_columns),
                        initial_indent=indent,
                        subsequent_indent=indent
                        )
                    show_info[sort_key] = first_row + '\n' + episodes
                else:
                    show_info[sort_key] = first_row

            if args['--ask-inactive']:
                if series.status == 'Ended' and first_time:
                    set_status = ask (
                        '%s has ended, and all have been downloaded. Set as inactive? [y/n]: ' %
                        title)
                    if set_status == 'y':
                        series.set_inactive()

        keys = show_info.keys()
        keys.sort()
        for i in keys:
            print show_info[i]

    if args['calender']:
        if args['--no-color']:
            use_color = False
        else:
            use_color = True

        header_color = 17
        date_color_1 = 17
        date_color_2 = 0
        title_color_1 = 18
        title_color_2 = 0

        title_width = 20
        if args['--width']:
            console_columns = int(args['--width'])
        else:
            console_columns = int(os.popen ('stty size', 'r').read().split()[1])
        spacer = ' '
        calender_columns = console_columns - (title_width + len(spacer))
        today = datetime.datetime.today()
        days_chars = '.....::' # first char is monday
        monthstart = '|'
        marker = '+'

        # build date title row
        months_row = today.strftime('%b') + (' ' * calender_columns)
        days_row = ''
        daybefore = today - datetime.timedelta(days=1)
        today = datetime.datetime.today()
        for days in range(calender_columns):
            cur_date = today + datetime.timedelta(days=days)

            if cur_date.month != daybefore.month:
                days_row = days_row + monthstart
                month = cur_date.strftime('%b')
                month_len = len(month)
                months_row = months_row[:days] + month + months_row[(days + month_len):]
            else:
                days_row = days_row + days_chars[cur_date.weekday()]

            daybefore = cur_date

        months_row = months_row[:calender_columns] # chop off any extra spaces created by adding the months
        if use_color:
            months_row = U.hi_color(months_row, 225, header_color)
            days_row = U.hi_color(days_row, 225, header_color)
        months_row = (' ' * title_width) + (' ' * len(spacer)) + months_row
        days_row =  (' ' * title_width) + (' ' * len(spacer)) + days_row
        print months_row
        print days_row

        # build shows rows
        step = 3
        color_row = False
        counter = 1
        for series in AllSeries(provider):
            broadcast_row = ' ' * calender_columns
            title = U.snip(series.db_name, title_width).ljust(title_width)

            has_episode = False
            for i in series.series: # season
                for j in series.series[i]: # episode
                    b_date = series.series[i][j]['firstaired']
                    if not b_date:
                        continue  # some episode have no broadcast date?
                    split_date = b_date.split ('-')
                    broadcast_date = datetime.datetime(
                        int(split_date[0]), int(split_date[1]), int(split_date[2]))
                    if broadcast_date < today:
                        continue  # don't include episodes before today
                    days_away = (broadcast_date - today).days + 1
                    broadcast_row = broadcast_row[:days_away] + marker + broadcast_row[(days_away + 1):]

                    has_episode = True

            row = title + spacer + broadcast_row[:calender_columns]
            if has_episode or args['--show-all']:
                if use_color and color_row:
                    title = U.hi_color(title, 225, title_color_1)
                    broadcast_row = U.hi_color(broadcast_row, 225, date_color_1)
                elif use_color and not color_row:
                    title = U.hi_color(title, 225, title_color_2)
                    broadcast_row = U.hi_color(broadcast_row, 225, date_color_2)
                row = title + spacer + broadcast_row
                print row

                if counter >= step:
                    counter = 0
                    color_row = True
                else:
                    color_row = False
                    counter = counter + 1

    if args['showmissing']:
        fp = FancyPrint()
        for series in AllSeries(provider):
            if series.is_missing():
                fp.standard_print (series.show_missing())
            else:
                fp.fancy_print ('Show up to date: %s' % (series.db_name))
        fp.done()

    if args['download']:
        for series in AllSeries(provider):
            series.download_missing()

    if args['addnew']:
        newShow = Series (provider, show_type='new')
        newShow.add_new (name=args['SHOW_NAME'])

    if args['nondbshow']:
        nons = Series (provider, show_type='nondb')
        nons.non_db (args['SEARCH_STRING'])

    if args['editdbinfo']:
        edit_db (args['SHOW_NAME'])

    if args['providers']:
        providers = config.providers
        for p in providers:
            print p, '  http://%s' % p.replace('_', '.')


if __name__ == '__main__':

    args = docopt(__doc__, version='0.1')
    init(args)
