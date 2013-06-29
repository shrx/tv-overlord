#!/usr/bin/env python

import StringIO
import datetime
import os
import re
import sqlite3
import time
import urllib, urllib2
from argparse import ArgumentParser
import pprint

from Util import U
from get_nzb_config import config
from get_nzb_util import FancyPrint
from get_nzb_util import Ask
from get_nzb_util import RT
import NZBMatrix
import tmdb
# import imdb
# from rottentomatoes import RT

def add (name):
	movies = tmdb.MovieDb()
	results = movies.search(name)

	# for i in results:
		# print ''
		# print i['name']
		# print i['overview']
		# print i['released']
		# print i['id']
		# print i['imdb_id']

	# print '>>>>>', results

	tbl = Ask()
	tbl.set_title ('Choose Movie')
	tbl.header_item ('Movie Name', width=30)
	tbl.header_item ('Overview', width=0)
	tbl.header_item ('Release Date', width=12)
	tbl.set_return_field (4)
	for i in results:
		overview = i['overview']
		if overview == None:
			overview = ''
		released = i['released']
		if released == None:
			released = ''
		tbl.set_row ([i['name'], overview, released, i['id']])

	print
	tmdb_id = tbl.ask()

	movie_name = overview = release_date = imdb_id = ''
	for i in results:
		if i['id'] == tmdb_id:
			movie_name = i['name']
			overview = i['overview']
			release_date = i['released']
			tmdb_id = i['id']
			imdb_id = i['imdb_id']

	sql = '''INSERT INTO movies (name, downloaded, overview, release_date, themoviedb_id, imdb_id)
			 VALUES (:movie_name, :downloaded, :overview, :release_date, :tmdb_id, :imdb_id)'''
	conn = sqlite3.connect (config.db_file)
	curs = conn.cursor()
	values = {'movie_name':movie_name, 'downloaded':'False', 'overview':overview,
			  'release_date':release_date, 'tmdb_id':tmdb_id, 'imdb_id':imdb_id}
	curs.execute (sql, values)

	conn.commit()
	conn.close()

	print
	print '%s (%s) added.' % (movie_name, release_date)

def info():
	sql = '''SELECT name, imdb_id FROM movies WHERE downloaded="False" ORDER BY replace (name, "The ", "");'''
	conn = sqlite3.connect (config.db_file)
	curs = conn.cursor()
	ddata = curs.execute (sql)
	data = []
	for i in ddata:
		data.append (i)
	conn.commit()
	conn.close()

	rt = RT()
	icons = {
		'available':U.effects (['greenf',], '[!]'),
		'unanounced':U.effects (['redf', ], '[ ]'),
		'has_date':U.effects (['yellowf', ], '[-]')
	}
	print 'Available: %s, Unanounced: %s, Has date: %s' % (
		icons ['available'],
		icons ['unanounced'],
		icons ['has_date'],
	)
	for i in data:
		name = i[0]

		imdb_id = i[1].replace ('tt', '')
		details = rt.imdb_details (imdb_id)
		not_anounced = is_available = has_date = False

		release_date = ''
		try:
			release_date = details['release_dates']['dvd']
			has_date = True
		except KeyError:
			not_anounced = True

		if has_date:
			today = datetime.date.today()
			split_date = release_date.split ('-')
			release = datetime.date (
				int (split_date[0]), int (split_date[1]), int (split_date[2]))
			if release < today:
				is_available = True
			else:
				diff = release - today


		name_just = 30
		note_just = 10
		name = name.strip()
		name = U.snip (name, name_just)
		name = name.ljust (name_just + 1)
		name = U.effects (['whitef'], name)

		if is_available:
			icon = icons['available'] #'[!]'
			note = 'Available'.ljust (note_just)
			note = U.effects (['whitef'], 'Available')
			# print '%s %s %s' % (icon, name, note)
			print '%s %s' % (icon, name)

		elif has_date:
			icon = icons['has_date'] # '[-]'
			rdate = U.effects (['whitef'], release_date)
			note = (str (diff.days) + ' days away').ljust (note_just)
			note = U.effects (['cyanf'], note)
			print '%s %s %s, %s' % (icon, name, rdate, note)

		elif not_anounced:
			icon = icons['unanounced'] # '[x]'
			note = 'Unanounced'.ljust (note_just)
			note = U.effects (['whitef'], note)
			print '%s %s %s' % (icon, name, note)

		# tbl.set_row (row)
		# print row
	# tbl.ask()


def get():
	sql = '''SELECT name, imdb_id FROM movies WHERE downloaded="False" ORDER BY replace (name, "The ", "");'''
	conn = sqlite3.connect (config.db_file)
	# conn.row_factory = dict_factory
	curs = conn.cursor()
	ddata = curs.execute (sql)
	data = []
	for i in ddata:
		data.append (i)
	conn.commit()
	conn.close()

	matrix = NZBMatrix.Matrix (username='smmcg', apiKey=config.nzbmatrix_apikey)
	# print data
	for i in data:		# each db row
		search_string = i[0]
		MOVIES_ALL = 'movies-all'
		results = matrix.Search (search_string, catId=MOVIES_ALL,
								 smaller=config.movie_max_size, larger=500)
		options = results['data'].values()

		tbl = Ask()
		tbl.set_title (search_string)

		tbl.header_item ('Movie Name', width=0)
		tbl.header_item ('Category', width=20)
		tbl.header_item ('Hits', width=5, align='right')
		tbl.header_item ('Size', width=10, align='right')
		tbl.header_item ('Comments', width=8)
		tbl.set_return_field (6)

		for j in options:
			category = j['CATEGORY']
			size = U.pretty_filesize (j['SIZE'])

			tbl.set_row ([j['NZBNAME'], category,
						 j['HITS'], size, j['COMMENTS'], j['NZBID']])

		print
		download_name = tbl.ask()
		print download_name


def init(args):
	# print args

	if args.action == 'add':
		add (args.search_string)

	elif args.action == 'info':
		info()

	elif args.action == 'get':
		get()

	else:
		print args.action, 4


if __name__ == '__main__':

	class t:
		add = 'add'
		info = 'info'
		get = 'get'
		class action:
			title = 'action'
			choices = ['add', 'info', 'get']
			help = '''Add a movie to the db, Get
				info about release times,
				or download available movies'''

	parser = ArgumentParser (
		description='''Download and manage movies
			when they are released on DVD.''')

	sub = parser.add_subparsers (
		title='Command help',
		description='description here',
		dest='action',
	)
	# add
	sub1 = sub.add_parser (
		'add',
		help='add help'
	)
	sub1.add_argument (
		'search_string',
		metavar='SEARCH_STRING',
		help='The name of the movie to search for'
	)
	# info
	sub2 = sub.add_parser (
		'info',
		help='info help'
	)

	# get
	sub3 = sub.add_parser (
		'get',
		help='get help'
	)


	args = parser.parse_args()
	init (args)

