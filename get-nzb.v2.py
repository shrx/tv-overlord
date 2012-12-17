#!/usr/bin/python

import StringIO
import datetime
from dateutil import parser as dateParser
import gzip
import os
import re
import sqlite3
import time
from argparse import ArgumentParser
import tvdb_api
import pprint
import textwrap

import sys
from ConsoleInput import ask_user as ask
import NZBMatrix
from get_nzb_config import config
from get_nzb_util import FancyPrint
from Util import U

# http://nzbmatrix.info/  <-- status info page
# http://docs.python.org/release/3.0.1/library/string.htm  String formating
# https://github.com/dbr/tvdb_api/wiki


def se_ep (season, episode):
	season = str (season).rjust (2, '0')
	episode = str (episode).rjust (2, '0')
	fixed = 'S%sE%s' % (season, episode)
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

	def __init__ (self, dbdata=[], show_type='current'):
		typelist = ('new', 'nondb', 'current')
		if show_type not in typelist:
			raise exception ('incorrect show type')
		if show_type == 'current':
			self._set_db_data (dbdata)
			self._get_thetvdb_series_data()
			self.matrix = NZBMatrix.Matrix (username='smmcg', apiKey=config.nzbmatrix_apikey)
		if show_type == 'nondb':
			self.matrix = NZBMatrix.Matrix (username='smmcg', apiKey=config.nzbmatrix_apikey)

		self.console_rows, self.console_columns = os.popen ('stty size', 'r').read().split()

	def _set_db_data (self, dbdata):
		'''Add the data from the local db'''
		self.db_name = dbdata['name']
		self.db_thetvdb_series_id = dbdata['thetvdb_series_id']
		self.db_current_season = dbdata['season']
		self.db_last_episode = dbdata['episode']
		self.db_nzbmatrix_search_name = dbdata['nzbmatrix_search_name']
		self.db_status = dbdata['status']

	def _get_thetvdb_series_data (self):
		'''Dynamicaly add all the data from Thetvdb.com'''
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
		# print missing
		if self.db_nzbmatrix_search_name:
			search_title = self.db_nzbmatrix_search_name
		else:
			search_title = self.db_name

		# if self does not have the attirbute series
		# its because of an error in the xml downloaded
		# from thetvdb site
		if not hasattr (self, 'series'):
			return

		for episode in missing:
			search_strings = [
				'%s %s' % (search_title, se_ep (episode['season'], episode['episode'])),
				'%s %sx%s' % (search_title, episode['season'], episode['episode'].zfill(2))
			]
			XVID = 6			# the nzb api uses 6 for XVID
			ALLTV = 'tv-all'	# the nzb api uses 'tv-all' for all tv catigories
			nzbid = None

			showlist = []
			error_a = error_b = False
			# The nzb api doesn't allow 'OR' searches so two searches are required.
			for search_string in search_strings:
				try:
					results = self.matrix.Search (search_string, catId=ALLTV, smaller=config.tv_max_size)
					headers = results['header']
					print '%s of %s api calls left' % (headers['api_rate_limit_left'], headers['api_rate_limit'])
					options = results['data'].values()
					for i in options:
						showlist.append (i)
				except NZBMatrix.MatrixError as inst:
					error_a = True

			if showlist:
				nzbid = self._ask (
					showlist,
					season=episode['season'],
					episode=episode['episode'])
			else:
				print '"%s" or "%s" are listed in TheTVDB, but not found at NZBMatrix' % (
					search_strings[0], search_strings[1])

			if nzbid == 'skip_rest':
				return

			if nzbid == 'mark':
				# mark the episode as watched, but don't download it
				self._update_db (season=episode['season'], episode=episode['episode'])
				continue

			if not nzbid:
				continue

			self._download_nzb (nzbid)
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
			se = se_ep (s['season'], s['episode'])
			missing_list.append (se)
		ret += textwrap.fill (', '.join (missing_list), width=int(self.console_columns),
							  initial_indent=indent, subsequent_indent=indent)
		return ret

	def add_new (self, name, season=1, episode=0):
		# search thetvdb
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
			self._add_new_db (season=season, episode=episode)

	def non_db (self, search_str):
		self.db_name = search_str
		try:
			nzbid = self._ask (self.matrix.Search (search_str)['data'].values(), None, None)
			if not nzbid: return
		except NZBMatrix.MatrixError:
			print 'No matches'
			return
		self._download_nzb (nzbid)


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

		for i in self.series:			# for each season
			for j in self.series[i]:	# for each episode
				b_date = self.series[i][j]['firstaired']
				if not b_date: continue	 # some episode have no broacast date?
				split_date = b_date.split ('-')
				broadcast_date = datetime.date (
					int (split_date[0]), int (split_date[1]), int (split_date[2]))
				if broadcast_date >= today:  # unaired future date
					break

				last_season = self.series[i][j]['seasonnumber']
				last_episode = self.series[i][j]['episodenumber']
				last_broadcast = se_ep (last_season, last_episode)
				if (last_watched < last_broadcast):
					# missing.append (se_ep (last_season, last_episode))
					missing.append ({'season':last_season, 'episode':last_episode})

		return missing

	def _ask (self, shows, season, episode):
		num_w = 2
		size_w = 10
		date_w = 12
		hits_w = 6
		title_w = int (self.console_columns) - (size_w + hits_w + date_w + 6)

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

		# Title bar row
		print
		# show_title = '%s %s' % (U.effects (['boldon',], self.db_name), 'SXXEXX')
		if season and episode:
			show_title = '%s %s' % (self.db_name, se_ep (season, episode))
		else:
			show_title = self.db_name

		print U.effects (['boldon'], U.hi_color (
			show_title.ljust (int (self.console_columns)),
			foreground=color.title_fg,
 			background=color.title_bg,
			))

		# Table header row
		print title_bar.join ([
			U.hi_color (' '.rjust (num_w), background=color.tb_header_bg),
			U.hi_color ('NZB Name'.ljust (title_w),
						background=color.tb_header_bg, foreground=color.tb_header_fg),
			U.hi_color ('Size'.ljust (size_w),
						background=color.tb_header_bg, foreground=color.tb_header_fg),
			U.hi_color ('Hits'.ljust (hits_w),
						background=color.tb_header_bg, foreground=color.tb_header_fg),
			U.hi_color ('Date'.ljust (date_w),
						background=color.tb_header_bg, foreground=color.tb_header_fg),
		])

		# [{'NZBNAME': 'Californication S04E12 HDTV XviD LOL', 'CATEGORY': 'TV > Divx/Xvid', 'HITS': '0',
		#   'GROUP': 'alt.binaries.teevee', 'LANGUAGE': 'English', 'NFO': 'yes',
		#   'IMAGE': '', 'INDEX_DATE': '2011-03-28 01:29:33', 'USENET_DATE': '2011-03-28 1:29:34',
		#   'WEBLINK': '', 'LINK': 'nzbmatrix.com/nzb-details.php?id=886802&hit=1',
		#   'COMMENTS': '0', 'NZBID': '886802', 'REGION': '0', 'SIZE': '279120445.44'}]

		# Matched episodes
		key = ('1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i',
			   'j','k','l','n','o','p','q','r','s','t','u','v','w','x','y','z')
		for row, counter in zip (shows, key):
			size = U.pretty_filesize (row['SIZE'])
			size = size.rjust (size_w)
			size = size.replace ('GB', U.fg_color ('yellow', 'GB'))

			title = U.snip (row['NZBNAME'].ljust (title_w), title_w)
			title = title.replace ('avi', U.fg_color ('green', 'avi'))

			date = row['USENET_DATE'].split (' ')[0]
			print bar.join ([
				counter.rjust (num_w),
				title,
				size,
				# U.snip (row['HITS'].ljust (hits_w), hits_w),
				row['HITS'].ljust (hits_w),
				U.snip (date.ljust (date_w), date_w),
			])

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
			if choice not in range (len (shows)):
				U.wr ('Number not between 1 and %s' % (len (shows)))
				return
		elif get == 'm':    # mark show as watched, but don't download it
			return 'mark'
		elif get == '[enter]':  # default #1
			choice = 0
		else:
			print 'Wrong choice'
			return

		return shows[choice]['NZBID']

	def _download_nzb (self, show_id):
		msg = U.hi_color ('Downloading nzb...', foreground=16, background=184)
		sys.stdout.write (msg)
		sys.stdout.flush()

		headers = self.matrix.Download (nzbId=show_id, dest=config.staging)

		backspace = '\b' * len (msg)
		filename = re.findall ('filename="(.*?)"',
							   headers['content-disposition'])[0]
		done = U.hi_color (filename.ljust (len (msg)), foreground=34)#34
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

	def _add_new_db (self, season, episode):
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
	def __init__ (self):
		self.dbdata = self._query_db()
		self.index = len (self.dbdata)
		self.i = 0
	def __iter__ (self):
		return self
	def next (self):
		if self.i == len (self.dbdata):
			raise StopIteration
		series = Series (dbdata=self.dbdata[self.i])
		self.i = self.i + 1
		return series

	def _query_db (self):
		sql = "SELECT name, season, episode, thetvdb_series_id, nzbmatrix_search_name, status \
			FROM shows WHERE status='active' ORDER BY replace (name, 'The ', '');"
		# sql = "SELECT name, season, episode, thetvdb_series_id \
			# FROM shows ORDER BY replace (name, 'The ', '');"
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
	sql = 'SELECT * FROM shows WHERE name LIKE :search'
	conn = sqlite3.connect (config.db_file)
	conn.row_factory = dict_factory
	curs = conn.cursor()
	search_str = '%%%s%%' % search_str
	values = {'search': search_str}
	data = curs.execute (sql, values)
 	for row in data:
		print 'Name:', row['name'], '--',
		print 'Season:', row['season'], '--',
		print 'Episode:', row['episode'], '--',
		print 'Status:', row['status'], '--',
		print 'NZBMatrix search title:', row['nzbmatrix_search_name']
		print

		new_name = raw_input ('Name (%s): ' % (row['name']))
		if not new_name:
			new_name = row['name']

		new_nzbmatrix_name = raw_input ('NZB search name (%s): ' % (row['nzbmatrix_search_name']))
		if not new_nzbmatrix_name:
			new_nzbmatrix_name = row['nzbmatrix_search_name']

		new_season = raw_input ('Season (%s): ' % (row['season']))
		if not new_season:
			new_season = row['season']

		new_episode = raw_input ('Episode (%s): ' % (row['episode']))
		if not new_episode:
			new_episode = row['episode']

		new_status = raw_input ('Status (%s): ' % (row['status']))
		if not new_status:
			new_status = row['status']

		sql = '''UPDATE shows SET name=:name, season=:season,
			episode=:episode, status=:status, nzbmatrix_search_name=:nzbmatrix_search_name
			WHERE thetvdb_series_id=:tvdb_id'''

		row_values = {'name':new_name, 'season':new_season, 'episode':new_episode,
					  'status':new_status, 'nzbmatrix_search_name':new_nzbmatrix_name,
					  'tvdb_id':row['thetvdb_series_id']}
		curs.execute (sql, row_values)

	conn.commit()
	conn.close()

def init (args):

	# print args
	# exit()

	if args.db_file:
		config.db_file = args.db_file
	if args.location:
		config.staging = args.location
	if args.no_cache == False:
		config.use_cache = False

	if args.action == t.info:
		for series in AllSeries():
			title = '%s' % (U.effects (['boldon', 'greenf'], series.db_name))
			if series.status == 'Ended':
				status = U.hi_color (series.status, foreground=196)
			else:
				status = U.hi_color ('Continuing', foreground=18)

			se = 'S%sE%s' % (
				str (series.db_current_season).rjust (2, '0'),
				str (series.db_last_episode).rjust (2,'0'),
			)
			# first row
			print '%s, %s, %s' % (
				title,
				se,
				status,
			)

			today = datetime.datetime.today()
			first_time = True
			episodes_list = []

			for i in series.series:
				for j in series.series[i]:
					b_date = series.series[i][j]['firstaired']
					if not b_date: continue	 # some episode have no broacast date?
					split_date = b_date.split ('-')
					broadcast_date = datetime.datetime (
						int (split_date[0]), int (split_date[1]), int (split_date[2]))

					# diff1 = broadcast_date - today,
					# print diff1
					# if diff1.days < -1:
					if broadcast_date < today:
						continue
					if first_time:
						first_time = False

					future_date = dateParser.parse (series.series[i][j]['firstaired'])
					diff = future_date - today
					fancy_date = future_date.strftime ('%b %-d')

					episodes_list.append ('S%sE%s, %s (%s)' % (
						series.series[i][j]['seasonnumber'].rjust (2, '0'),
						series.series[i][j]['episodenumber'].rjust (2, '0'),
						fancy_date,
						diff.days,
					))

			if not first_time:
				# list_title = U.hi_color ('Future episodes: ', foreground=34)
				# indent = U.effects (['boldon'], U.hi_color ('    Future episodes: ', foreground=28))
				# indent = U.effects (['boldon'], '    Future episodes: ')
				# indent = '    Future episodes: '
				indent = '    '
				episode_list = 'Future episodes: ' + ' - '.join (episodes_list)
				print textwrap.fill (
					U.hi_color (episode_list, foreground=22),
					width=int(series.console_columns),
					initial_indent=indent,
					subsequent_indent=indent
				)

			if args.ask_inactive:
				if series.status == 'Ended' and first_time:
					set_status = ask ('Series ended, and all have been downloaded. Set as inactive? [y/n]: ')
					if set_status == 'y':
						series.set_inactive()

			'''
			S05E01, Jun 10 (48) - S05E02, Jun 17 (55)

			if show ended:                           series.status == ended
			    if still watching:                   db.status == active
			        get shows left in season         series.shows_left_in_season
				    get seasons left                 series.seasons_left
			    ? else:                              db.status == inactive
			        ? set show status to INACTIVE
			else show still running:                 series.status == continuing
			    if still watching:
			        get shows left in season
			    ? else done watching:
			        ? set show status to INACTIVE

			'''

			'''
			Torchwood S04E11, Continuing
			Battlestar Galactica (2002) S03E03, Ended
			  S07E19 S07E20 S07E21 S07E22 S07E23
			'''

			'''
			Torchwood
			  S04E11, Continuing
			  Left in season: 6
			Battlestar Galactica (2002)
			  S03E03, Ended, Last episode: S05E12
			  Left in season: 9; Seasons left: 3
			'''


	if args.action == t.showmissing:
		fp = FancyPrint()
		for series in AllSeries():
			if series.is_missing():
				fp.standard_print (series.show_missing())
			else:
				fp.fancy_print ('Show up to date: %s' % (series.db_name))
		fp.done()


	if args.action == t.download: #'download':
		if args.max_size:
			config.tv_max_size = args.max_size

		for series in AllSeries():
			series.download_missing()

	if args.action == t.addnew:
		# print args
		newShow = Series (show_type='new')
		newShow.add_new (name=args.search_string,
						 season=args.season_number,
						 episode=args.episode_number)

	if args.action == t.nondbshow:
		nons = Series (show_type='nondb')
		nons.non_db (args.search_string)

	if args.action == t.editdbinfo:
		edit_db (args.search_string)


if __name__ == '__main__':

	class t:
		download = 'download'
		info = 'info'
		showmissing = 'showmissing'
		addnew = 'addnew'
		nondbshow = 'nondbshow'
		editdbinfo = 'editdbinfo'

	parser = ArgumentParser (
		description='Download and manage tv shows and movies'
	)
	parser.add_argument (
		'-d', '--db-file',
		metavar='db-file',
		help='Use a different database than the default one',
	)
	parser.add_argument (
		'-l', '--location',
		metavar='download_location',
		help='Set the download location',
	)
	parser.add_argument (
		'-n', '--no-cache',
		action='store_false',
		help='If set, do not use the local thetvdb cache'
	)
	parser.add_argument (
		'--search-method-a-only',
		action='store_true',
		help='Search using SXXEXX pattern only instead of both SXXEXX and SxXX'
	)
	sub = parser.add_subparsers (
		title='Command help',
		description='Use one of the following commands.  For aditional help, \
			use <command> -h for help with a specific command',
		dest='action',
	)

	# download
	par1 = sub.add_parser (
		t.download,
		help='Download any new shows available.  Optionally, \
			download a single show',
	)
	par1.add_argument (
		'-i', '--series-id',
		help='The series id can be used to specify a single \
			show to download'
	)
	par1.add_argument (
		'-m', '--max-size',
		default=2000, type=int,
		help='Set the max size in kilobytes'
	)

	# info
	par2 = sub.add_parser (
		t.info,
		help='Display information stored in the local db; last \
			episode downloaded, show status (canceled, etc...), \
			episodes in current season, etc...'
	)
	par2.add_argument (
		'-a', '--ask-inactive',
		action='store_true',
		help='Ask if shows that are ended, and all have been downloaded, should they be set to INACTIVE'
	)

	# showmissing
	par3 = sub.add_parser (
		t.showmissing,
		help='Display episodes ready to download',
	)
	par3.add_argument (
		'-i', '--series-id',
		help='The series id can be used to specify a single show',
	)

	# addnew
	par4 = sub.add_parser (
		t.addnew,
		help='Add a new show to download',
	)
	par4.add_argument (
		'search_string',
		metavar='SEARCH_STRING',
		help='The name of the show to add to the db',
	)
	par4.add_argument (
		'-s', '--season-number',
		# metavar='season-number',
		default='1',
		help='Specify the season to start downloading at.  If \
			not used, will default to season one',
	)
	par4.add_argument (
		'-e', '--episode-number',
		# metavar='episode-number',
		default='0',
		help='Specify the episode to start downloading at.  If \
			not used, will default to episode one',
	)

	# nondbshow
	par5 = sub.add_parser (
		t.nondbshow,
		help='Download a show or movie not in the db',
	)
	par5.add_argument (
		'search_string',
		metavar='SEARCH_STRING',
		help='The name of the show or movie to download',
	)

	# editdbinfo
	par6 = sub.add_parser (
		t.editdbinfo,
		help='Edit the information in the db for a single show',
	)
	par6.add_argument (
		'search_string',
		metavar='SEARCH_STRING',
		help= ('The name of the show to edit.  If more than one ' +
			   'show matches the SEARCH_STRING, edit multiple shows.'),
	)
	# change showname
	# change season, episode

	args = parser.parse_args()
	init (args)
