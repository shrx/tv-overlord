#!/usr/bin/env python3

import datetime
import os
import sqlite3
import textwrap

from pprint import pprint as pp
from dateutil import parser as date_parser
# from docopt import docopt
import click

from tvoverlord.allseries import AllSeries
from tvoverlord.series import Series
from tvoverlord.config import Config
from tvoverlord.tvutil import FancyPrint, dict_factory
from tvoverlord.util import U
from tvoverlord.location import Location
from tvoverlord.history import History


def edit_db(search_str):
    sql = 'SELECT * FROM shows WHERE name=:search'
    conn = sqlite3.connect(Config.db_file)
    conn.row_factory = dict_factory
    curs = conn.cursor()
    values = {'search': search_str}
    curs.execute(sql, values)
    row = curs.fetchone()

    if not row:
        print('"%s" not found' % search_str)
        exit()

    is_error = False

    print('While editing a field, hit <enter> to leave it unchanged.')
    print('Type "<ctrl> c" to cancel all edits.\n')
    try:
        new_name = input('Name: (%s) ' % (row['name']))
        if not new_name:
            new_name = row['name']

        new_search_engine_name = input('Search engine title: (%s) ' % (row['search_engine_name']))
        if not new_search_engine_name:
            new_search_engine_name = row['search_engine_name']

        new_season = input('Current season: (%s) ' % (row['season']))
        if not new_season:
            new_season = str(row['season'])

        new_episode = input('Last episode: (%s) ' % (row['episode']))
        if not new_episode:
            new_episode = str(row['episode'])

        new_status = input('Status: (%s) ' % (row['status']))
        if not new_status:
            new_status = row['status']

        print()

    except KeyboardInterrupt:
        print('\nDatabase edit canceled.')
        exit()

    if not new_season.isdigit():
        print('Error: Season must be a number')
        is_error = True

    if not new_episode.isdigit():
        print('Error: Episode must be a number')
        is_error = True

    if new_status not in ['active', 'inactive']:
        print('Error: Status must be either "active" or "inactive"')
        is_error = True

    if is_error:
        exit()

    sql = '''UPDATE shows SET name=:name, season=:season,
        episode=:episode, status=:status, search_engine_name=:search_engine_name
        WHERE thetvdb_series_id=:tvdb_id'''

    row_values = {'name': new_name, 'season': new_season, 'episode': new_episode,
                  'status': new_status, 'search_engine_name': new_search_engine_name,
                  'tvdb_id': row['thetvdb_series_id']}

    curs.execute(sql, row_values)

    print('Database updated')

    conn.commit()
    conn.close()

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
    'token_normalize_func': lambda x: x.lower(),
}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--no-cache', '-n', is_flag=True,
              help='Re-download the show data instead of using the cached data.')
def tvol(no_cache):
    """Download and manage tv shows.

    Use `tvol COMMAND -h` to get help for each command.

    \b
    TVOverlord source code is available at
    https://github.com/8cylinder/tv-overlord
    Any feature requests or bug reports should go there.
    """
    if no_cache:
        Config.use_cache = False
    else:
        Config.use_cache = True


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('show_name', required=False)
@click.option('--show-all', '-a', is_flag=True,
              help='Show all shows including the ones marked inactive.')
@click.option('--sort-by-next', '-x', is_flag=True,
              help='Sort by release date instead of the default alphabetical.')
@click.option('--ask-inactive', is_flag=True,
              help='Ask to make inactive shows that are cancelled.')
@click.option('--show-links', is_flag=True,
              help='Show links to IMDB.com and TheTVDb.com for each show.')
@click.option('--synopsis', is_flag=True,
              help='Display the show synopsis.')
def info(show_name, show_all, sort_by_next,
         ask_inactive, show_links, synopsis):
    """Show information about your tv shows.

    SHOW_NAME can be a full or partial name of a show.  If used, it
    will show information about any shows that match that string, else
    it will show informaton about all your shows.
    """
    show_info = {}
    counter = 0

    # When the user specifies a single show, turn on --show-all
    # because the show they are asking for might an inactive show
    # and turn on --synopsis and --show-links since its only one
    # show we may as well show everything
    filter_name = ''
    if show_name:
        show_all = True
        synopsis = True
        show_links = True
        filter_name = show_name

    all_shows = AllSeries(name_filter=filter_name)
    for series in all_shows:
        title = series.db_name

        # check if the series object has a status attribute. if it
        # doesn't then its probably a show that nothing is known
        # about it yet.
        if 'status' not in dir(series):
            continue

        if series.status == 'Ended':
            status = U.hi_color(series.status, foreground=196)
        else:
            status = ''

        # build first row of info for each show
        se = 'Last downloaded: S%sE%s' % (
            str(series.db_current_season).rjust(2, '0'),
            str(series.db_last_episode).rjust(2, '0'),
        )
        se = U.hi_color(se, foreground=48)

        imdb_url = thetvdb_url = ''
        if show_links:
            imdb_url = U.hi_color('\n    IMDB.com:    http://imdb.com/title/%s' % series.imdb_id, foreground=20)
            thetvdb_url = U.hi_color('\n    TheTVDB.com: http://thetvdb.com/?tab=series&id=%s' % series.id,
                                     foreground=20)

        if synopsis and series.overview:
            paragraph = series.overview
            indent = '    '
            if int(series.console_columns) < fill_width:
                fill_width = series.console_columns
            paragraph = textwrap.fill(paragraph,
                                      initial_indent=indent,
                                      subsequent_indent=indent)
            synopsis = '\n%s' % paragraph

        first_row_a = []
        fancy_title = U.effects(['boldon'], title)
        for i in [fancy_title + ',', se, status, imdb_url, thetvdb_url, synopsis]:
            if i: first_row_a.append(i)
        first_row = ' '.join(first_row_a)

        # build 'upcoming episodes' list
        today = datetime.datetime.today()
        first_time = True
        episodes_list = []
        counter += 1
        for i in series.series:  # season
            for j in series.series[i]:  # episode
                b_date = series.series[i][j]['firstaired']
                if not b_date: continue  # some episode have no broadcast date?

                split_date = b_date.split('-')
                broadcast_date = datetime.datetime(
                    int(split_date[0]), int(split_date[1]), int(split_date[2]))

                if not show_all:
                    if broadcast_date < today:
                        continue

                future_date = date_parser.parse(b_date)
                diff = future_date - today
                fancy_date = future_date.strftime('%b %-d')
                if broadcast_date >= today:
                    episodes_list.append('S%sE%s, %s (%s)' % (
                        series.series[i][j]['seasonnumber'].rjust(2, '0'),
                        series.series[i][j]['episodenumber'].rjust(2, '0'),
                        fancy_date,
                        diff.days + 1,
                    ))

                if first_time:
                    first_time = False
                    if sort_by_next:
                        sort_key = str(diff.days).rjust(5, '0') + str(counter)
                    else:
                        sort_key = series.db_name.replace('The ', '')

        if not first_time:
            if episodes_list:
                indent = '    '
                episode_list = 'Future episodes: ' + ' - '.join(episodes_list)
                episodes = textwrap.fill(
                    U.hi_color(episode_list, foreground=22),
                    initial_indent=indent,
                    subsequent_indent=indent
                )
                show_info[sort_key] = first_row + '\n' + episodes
            else:
                show_info[sort_key] = first_row

        if ask_inactive:
            if series.status == 'Ended' and first_time:
                click.echo(
                    '%s has ended, and all have been downloaded. Set as inactive? [y/n]: ' %
                    title)
                set_status = click.getchar()
                click.echo(set_status)
                if set_status == 'y':
                    series.set_inactive()

    keys = list(show_info.keys())
    keys.sort()
    full_output = ''
    for i in keys:
        full_output = full_output + show_info[i] + '\n\n'
    click.echo_via_pager(full_output)


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('show_name', required=False)
@click.option('--show-all', '-a', is_flag=True,
              help='Show all shows including the ones marked inactive.')
@click.option('--sort-by-next', '-x', is_flag=True,
              help='Sort by release date instead of the default alphabetical.')
@click.option('--no-color', is_flag=True,
              help="Don't use color in output.  Useful if output is to be used in email or text file.")
@click.option('--days',
              help='The number of days to show in the calendar.')
def calendar(show_name, show_all, sort_by_next, no_color, days):
    """Display a calendar of upcoming episodes.

    If SHOW_NAME is used, it will display a calendar for any shows that
    match that string.

    --days can be one number or two numbers.  If one number is used, it will
    show that many days ahead.  If two numbers are used, the first number is
    where the calendar will start and the second number is where it will end.
    The two number must be seperated by a comma with no spaces.

    \b
    --days 10      will show from today to 10 days in the future
    --days 10,20   will start ten days from now and then show 20 days ahead.
    --days -20,10  will go back 20 days from today and then show ahead from there.
    """
    if no_color:
        use_color = False
    else:
        use_color = True

    # set colors for ui elements
    header_color = 17
    date_color_1 = 17
    date_color_2 = 0
    title_color_1 = 18
    title_color_2 = 0

    title_width = 20  # width of show titles column
    console_columns = int(os.popen('stty size', 'r').read().split()[1])
    spacer = ' '  # can be any string, any length
    today = datetime.datetime.today()

    if days:
        days = days.split(',')
        days = [int(x) for x in days]
        if len(days) == 2:
            today = today + datetime.timedelta(days=days[0])
            calendar_columns = days[1]
        if len(days) == 1:
            calendar_columns = days[0]
    else:
        calendar_columns = console_columns - (title_width + len(spacer))

    # Days_chars can be any string of seven chars. eg: 'mtwtfSS'
    days_chars = '.....::'  # first char is monday
    monthstart = '|'  # marker used to indicate the begining of month

    # build date title row
    months_row = today.strftime('%b') + (' ' * calendar_columns)
    days_row = ''
    daybefore = today - datetime.timedelta(days=1)
    for days in range(calendar_columns):
        cur_date = today + datetime.timedelta(days=days)

        if cur_date.month != daybefore.month:
            days_row += monthstart
            month = cur_date.strftime('%b')
            month_len = len(month)
            months_row = months_row[:days] + month + months_row[(days + month_len):]
        else:
            days_row += days_chars[cur_date.weekday()]

        daybefore = cur_date

    months_row = months_row[:calendar_columns]  # chop off any extra spaces created by adding the months
    if use_color:
        months_row = U.hi_color(months_row, 225, header_color)
        days_row = U.hi_color(days_row, 225, header_color)
    months_row = (' ' * title_width) + (' ' * len(spacer)) + months_row
    days_row = (' ' * title_width) + (' ' * len(spacer)) + days_row
    print(months_row)
    print(days_row)

    # build shows rows
    step = 3
    color_row = False
    counter = 1
    season_marker = '-'
    filter_date = ''
    filter_name = ''
    if sort_by_next:
        filter_date = True
    if show_name:
        filter_name = show_name

    all_series = AllSeries(name_filter=filter_name, by_date=filter_date)
    for series in all_series:
        broadcast_row = ''
        title = series.db_name[:title_width].ljust(title_width)
        has_episode = False
        first_display_date = True
        last_days_away = 0
        last_date = 0
        for i in series.series:  # season
            for j in series.series[i]:  # episode
                episode_number = series.series[i][j]['episodenumber']
                b_date = series.series[i][j]['firstaired']
                if not b_date:
                    continue  # some episode have no broadcast date?
                split_date = b_date.split('-')
                broadcast_date = datetime.datetime(
                    int(split_date[0]), int(split_date[1]), int(split_date[2]))
                if broadcast_date == last_date:
                    continue  # sometimes multiple episodes have the same date, don't repeat them.
                last_date = broadcast_date
                if broadcast_date.date() < today.date():
                    continue  # don't include episodes before today
                days_away = (broadcast_date - today).days + 1
                if days_away >= calendar_columns:
                    continue  # don't include days after the width of the screen
                if series.series[i][j]['seasonnumber'] == '0':
                    continue  # not interested in season 0 episodes.

                if first_display_date:
                    if int(episode_number) > 1:
                        before_first = season_marker * days_away
                    else:
                        before_first = ' ' * days_away
                    broadcast_row = before_first + episode_number
                    first_display_date = False
                    # set the next episode date in the db while we're here:
                    series.set_next_episode(broadcast_date.date())
                else:
                    episode_char_len = len(str(int(episode_number) - 1))
                    broadcast_row = broadcast_row + (
                        season_marker * (days_away - last_days_away - episode_char_len)) + episode_number

                last_days_away = days_away

                has_episode = True

        broadcast_row = broadcast_row[:calendar_columns].ljust(calendar_columns)

        if has_episode or show_all:
            if use_color and color_row:
                title = U.hi_color(title, 225, title_color_1)
                broadcast_row = U.hi_color(broadcast_row, 225, date_color_1)
            elif use_color and not color_row:
                title = U.hi_color(title, 225, title_color_2)
                broadcast_row = U.hi_color(broadcast_row, 225, date_color_2)
            row = title + spacer + broadcast_row
            print(row)

            if counter >= step:
                counter = 0
                color_row = True
            else:
                color_row = False
                counter += 1


def tfunct(series):
    try:
        title = series.db_name
    except AttributeError:
        title = ''
    return title


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.option('--today', '-t', is_flag=True,
              help="Also show today's episodes.")
def showmissing(today):
    """List episodes that are ready to download.
    """
    fp = FancyPrint()

    all_series = AllSeries()
    with click.progressbar(
            all_series, item_show_func=tfunct, show_percent=False,
            show_eta=False, width=50, empty_char='\u00B7',
            fill_char=click.style('\u2588', fg='blue'),
    ) as bar:
        for series in bar:
            if series.is_missing(today):
                fp.standard_print(series.show_missing())
    fp.done()

@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('show_name', required=False)
@click.option('--today', '-t', is_flag=True,
              help="Also download today's episodes.")
@click.option('--ignore', '-i', is_flag=True,
              help="Ignore 'Not connected to vpn' warning.")
@click.option('--count', '-c', type=int, default=10,
              help='Number of search results to list. (default: 5)')
@click.option('--location', '-l',
              type=click.Path(exists=True, resolve_path=True),
              help='Directory to download the nzb files to.')
def download(show_name, today, ignore, count, location):
    """Download available episodes.

    If SHOW_NAME is used, it will download any shows that match that title
    """
    if Config.ip and not ignore:
        L = Location()
        if L.ips_match(Config.ip):
            print('%s not connected to VPN' % (U.effects(['redb', 'boldon'], ' Warning: ')))
            exit()
    all_series = AllSeries(name_filter=show_name)
    for series in all_series:
        series.download_missing(count, today)


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('show_name')
def addnew(show_name):
    """Add a new tv show to the database.

    The SHOW_NAME can be a partial name, but the more accurate the name
    the better the search will be.  It helps to add the year to the name
    as well.

    If you search for 'Doctor Who', the result will be the original series,
    but if you want the modern one, search for 'Doctor Who 2005'
    """
    new_show = Series(show_type='new')
    new_show.add_new(name=show_name)


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('search_string')
@click.option('--count', '-c', type=int, default=10,
              help='Number of search results to list. (default: 5)')
@click.option('--location', '-l',
              type=click.Path(exists=True, resolve_path=True),
              help='Directory to download the nzb files to.')
def nondbshow(search_string, count, location):
    """Download anything, ignoring the database.

    This just does a simple search and passes you choise to the bittorrent
    client.  The download is not recorded in the database.
    """
    nons = Series(show_type='nondb')
    nons.non_db(search_string, count)


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('show_name')
def editdbinfo(show_name):
    """Edit the contents of the database.

    This allows you to change the fields in the database for a show.
    The fields affected are:

    \b
    Name:                This is what is used for searching and folder names.
    Search engine title: Sometimes a different name searches better.  If this
                         is set, it will be used when searching.
    Current season:      Setting this can be usefull if you add a new show to
                         the db, but want to download starting at a later season.
    Last episode:        Set this to change the last episode downloaded.
    Status:              This can be 'active' or 'inactive'.  This can be used
                         to turn off a show.
    """
    edit_db(show_name)


def parse_history(criteria):
    # try to parse criteria as an int, then as a date.  If neither don't
    # work, pass it on as a string which should be a show title
    try:
        criteria = int(criteria)
    except:
        try:
            criteria = date_parser.parse(criteria)
        except:
            criteria = criteria
    return criteria


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('criteria', required=False)
@click.option('--what-to-show', '-w', type=str,
              help="An optional list of information to show seperated by commas.")
def history(criteria, what_to_show):
    """Show a list of downloaded episodes.

    CRITERIA can be days, a date or a show title.  If its days, it
    will show results from now to X days ago.  If it is a date, it
    will show downloads for that date, and if its a title or partial
    title, it will show all downloads for that show.

    \b
    what-to-show can be any of these:
    date, title, season, episode, magnet, oneoff, complete, filename, destination

    eg. --what-to-show 'title,filename,magnet'
    """
    if not criteria:
        criteria = 1
    criteria = parse_history(criteria)
    hist = History(criteria)
    hist.show(what_to_show)


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('criteria', required=False)
def copy(criteria):
    """Re copy a show to the library location.

    CRITERIA can be days, a date or a show title.  If its days, it
    will show results from now to X days ago.  If it is a date, it
    will show downloads for that date, and if its a title or partial
    title, it will show all downloads for that show.
    """
    if not criteria:
        criteria = 1
    criteria = parse_history(criteria)
    hist = History(criteria)
    hist.copy()


@tvol.command(context_settings=CONTEXT_SETTINGS)
@click.argument('criteria', required=False)
def redownload(criteria):
    """Re download a show.

    CRITERIA can be days, a date or a show title.  If its days, it
    will show results from now to X days ago.  If it is a date, it
    will show downloads for that date, and if its a title or partial
    title, it will show all downloads for that show.
    """
    if not criteria:
        criteria = 1
    criteria = parse_history(criteria)
    hist = History(criteria)
    hist.download()
