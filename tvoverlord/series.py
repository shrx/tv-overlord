import datetime
import sqlite3
import sys
import textwrap
import tvdb_api
from pprint import pprint as pp
import click

from tvoverlord.search import Search, SearchError
from tvoverlord.util import U
from tvoverlord.tvutil import style
from tvoverlord.config import Config
from tvoverlord.consoletable import ConsoleTable
from tvoverlord.tracking import Tracking
from tvoverlord.db import DB


class Series:
    """
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
    """

    def se_ep(self, season, episode):
        season_just = str(season).rjust(2, '0')
        episode = str(episode).rjust(2, '0')
        fixed = 'S%sE%s' % (season_just, episode)

        return fixed

    def __init__(self, dbdata=[], show_type='current'):
        typelist = ('new', 'nondb', 'current')
        if show_type not in typelist:
            raise Exception('incorrect show type')

        if show_type == 'current':
            self._set_db_data(dbdata)
            self._get_thetvdb_series_data()
            self.search_provider = Search()

        if show_type == 'nondb':
            self.search_provider = Search()

        self.console_columns = Config.console_columns

        self.db = DB()

    def _set_db_data(self, dbdata):
        """Add the data from the local db"""
        self.db_name = dbdata['name']
        self.db_thetvdb_series_id = dbdata['thetvdb_series_id']
        self.db_ragetv_series_id = dbdata['ragetv_series_id']
        self.db_current_season = dbdata['season']
        self.db_last_episode = dbdata['episode']
        # Sometimes the thetvdb name is slighly different than the
        # name to use for searching, thats why we use search_engine_name
        self.db_search_engine_name = dbdata['search_engine_name']
        self.db_status = dbdata['status']

    def _get_thetvdb_series_data(self):
        """Dynamicaly add all the data from Thetvdb.com

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

        """

        tv = tvdb_api.Tvdb(apikey=Config.thetvdb_apikey,
                           cache=Config.use_cache)
        try:
            series = tv[self.db_name]
            self.show_exists = True
        except KeyError:
            click.echo('TheTVDB is down or very slow, try again.')
            sys.exit()
        except tvdb_api.tvdb_shownotfound:
            click.echo('Show not found: %s' % self.db_name)
            self.show_exists = False
            return
        except tvdb_api.tvdb_error as e_msg:
            click.echo()
            click.echo('Error: %s' % self.db_name)
            click.echo('-----------------------------')
            click.echo(e_msg)
            return
        except UnboundLocalError as e:
            click.echo('+++++++++++++++++++++++++')
            click.echo(e)
            click.echo('+++++++++++++++++++++++++')

        for i in series.data:
            setattr(self, i, series.data[i])
        self.series = series

    def download_missing(self, episode_display_count, download_today=False):
        missing = self._get_missing(download_today)
        if self.db_search_engine_name:
            search_title = self.db_search_engine_name
        else:
            search_title = self.db_name

        # if self does not have the attirbute series
        # its because of an error in the xml downloaded
        # from thetvdb site
        if not hasattr(self, 'series'):
            return

        for episode in missing:
            showid = None
            results = self.search_provider.search(
                search_title,
                season=episode['season'],
                episode=episode['episode'],
                search_type=Config.search_type,
            )

            if results:
                showid = self._ask(
                    results,
                    display_count=episode_display_count,
                    season=episode['season'],
                    episode=episode['episode']
                )
            else:
                click.echo('"%s" is listed in TheTVDB, but not found in any search engines' % (
                    search_title))

            if showid == 'skip_rest':
                return
            elif showid == 'skip':
                continue
            elif showid == 'mark':
                # mark the episode as watched, but don't download it
                self._update_db(season=episode['season'],
                                episode=episode['episode'])
                continue

            self._download(showid)
            self._update_db(season=episode['season'],
                            episode=episode['episode'])

    def is_missing(self, download_today=False):
        missing = self._get_missing(download_today)
        self.missing = missing

        ret = True
        try:
            if len(missing) == 0:
                ret = False
        except:
            ret = False

        return ret

    def show_missing(self):
        missing = self.missing
        if len(missing) == 0:
            return False
        ret = style(self.db_name, fg='green', bold=True)
        ret += ' - %s, %s' % (self.airs_dayofweek, self.airs_time)
        ret += '\n'
        indent = '    '
        missing_list = []
        for s in missing:
            se = 'S%sE%s' % (s['season'].rjust(2, '0'),
                             s['episode'].rjust(2, '0'))
            missing_list.append(se)
        ret += textwrap.fill(', '.join(missing_list),
                             width=int(self.console_columns),
                             initial_indent=indent,
                             subsequent_indent=indent)
        return ret

    def add_new(self, name):
        self.db_name = name
        self._get_thetvdb_series_data()
        indent = '  '

        if not self.show_exists:
            sys.exit()

        click.echo()
        click.echo(self.seriesname)
        click.echo('-' * len(self.seriesname))
        if self.overview:
            click.echo(textwrap.fill(self.overview, initial_indent=indent,
                                subsequent_indent=indent))
        else:
            click.echo('No description provided.')
        click.echo()
        click.echo('%sFirst aired: %s' % (indent, self.firstaired))
        click.echo('%sStatus: %s' % (indent, self.status))
        click.echo()
        click.echo('Is this the correct show? [y/n]', nl=False)
        correct = click.getchar(echo=False)
        correct = correct.decode('utf-8')
        click.echo(' %s' % correct)

        if str(correct) == 'y':
            self._add_new_db()
            click.echo('Show added')
        else:
            click.echo('Not added')

    def non_db(self, search_str, display_count):
        self.db_name = search_str
        try:
            show_data = self._ask(
                self.search_provider.search(
                    search_str, search_type=Config.search_type),
                None, None, display_count)
            if not show_data:
                return
        except SearchError:
            click.echo('No matches')
            return
        self._download(show_data)

    def _get_missing(self, download_today=False):
        """Returns a list of missing episodes"""
        missing = []
        today = datetime.date.today()
        last_watched = self.se_ep(self.db_current_season, self.db_last_episode)

        # if SELF does not have the attribute: 'series'
        # it's because of an error in the xml downloaded
        # from thetvdb site
        if not hasattr(self, 'series'):
            return

        # Check the db_next_episode date and see if
        # we should check if a show is ready
        #   IF: a date is in the db and that date is less that today,
        # THEN: 'return' since its not time yet to check for new episodes
        if hasattr(self, 'db_next_episode'):
            next_date = self.db_next_episode.split('-')
            next_date = datetime.date(
                int(next_date[0]), int(next_date[1]), int(next_date[2])
            )
            if today <= next_date:
                return missing

        for i in self.series:  # for each season
            for j in self.series[i]:  # for each episode
                b_date = self.series[i][j]['firstaired']
                if not b_date:
                    continue  # some episode have no broacast date?
                split_date = b_date.split('-')
                broadcast_date = datetime.date(
                    int(split_date[0]), int(split_date[1]), int(split_date[2]))

                if not download_today:
                    # download yesterday's and older shows
                    if broadcast_date >= today:  # unaired future date
                        # since this date is the next future date, put
                        # this in the db so we can check for the next
                        # episode at that future date
                        self.set_next_episode(broadcast_date)
                        break
                else:
                    # download today's and older shows
                    if broadcast_date > today:  # unaired future date
                        self.set_next_episode(broadcast_date)
                        break

                last_season = self.series[i][j]['seasonnumber']
                last_episode = self.series[i][j]['episodenumber']
                last_broadcast = self.se_ep(last_season, last_episode)
                if last_season == '0' or last_episode == '0':
                    break  # don't display the S00E01 or S05E00 type special episodes

                if last_watched < last_broadcast:
                    missing.append({'season': last_season,
                                    'episode': last_episode})
        return missing

    def set_next_episode(self, next_date):
        sql = 'UPDATE shows SET next_episode=:next_date WHERE name=:show_name'
        conn = sqlite3.connect(Config.db_file)
        curs = conn.cursor()
        values = {'next_date': next_date.isoformat(), 'show_name': self.db_name}
        curs.execute(sql, values)
        conn.commit()
        conn.close()

    def _ask(self, shows, season, episode, display_count):
        click.echo()
        if season and episode:
            show_title = '%s %s' % (self.db_name, self.se_ep(season, episode))
        else:
            show_title = '%s' % shows[0][0][0]

        tbl = ConsoleTable(shows)
        tbl.set_title(show_title)
        tbl.set_count(display_count)
        show_to_dl = tbl.generate()

        # save data to Tracking
        tracking = Tracking()
        if show_to_dl not in ['skip', 'skip_rest', 'mark']:
            tracking.save(self.db_name, season, episode, shows, show_to_dl)

        return show_to_dl

    def _download(self, show_data):
        self.search_provider.download(
            chosen_show=show_data,
            destination=Config.staging,
            search_type=Config.search_type)

    def set_inactive(self):
        sql = '''UPDATE shows
                 SET status="inactive"
                 WHERE thetvdb_series_id=:tvdb_id'''
        conn = sqlite3.connect(Config.db_file)
        curs = conn.cursor()
        values = {'tvdb_id': self.db_thetvdb_series_id}
        curs.execute(sql, values)

        conn.commit()
        conn.close()

    def _update_db(self, season, episode):
        sql = """UPDATE shows
                 SET season=:season, episode=:episode
                 WHERE thetvdb_series_id=:tvdb_id"""
        conn = sqlite3.connect(Config.db_file)
        curs = conn.cursor()
        values = {'season': season, 'episode': episode,
                  'tvdb_id': self.db_thetvdb_series_id}
        curs.execute(sql, values)

        conn.commit()
        conn.close()

    def _add_new_db(self, season=0, episode=0):
        if self.db.show_exists(self.id):
            sql = '''UPDATE shows SET status="active"
                     WHERE thetvdb_series_id=:thetvdb_id;'''
            values = {'thetvdb_id': self.id}
            click.echo()
            click.echo('%s is already in the db. Its status is now set to "active"' % self.seriesname)
        else:
            sql = '''
                INSERT INTO shows (
                  network_status, status, thetvdb_series_id,
                  name, season, episode)
                VALUES (:network_status, :status, :thetvdb_id,
                        :name, :season, :episode)'''
            values = {'network_status': self.status,
                      'status': 'active',
                      'thetvdb_id': self.id,
                      'name': self.seriesname,
                      'season': season,
                      'episode': episode}
        conn = sqlite3.connect(Config.db_file)
        curs = conn.cursor()
        curs.execute(sql, values)
        conn.commit()
        conn.close()
