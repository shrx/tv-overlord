#!/usr/bin/env python
import os
import sys
import ConfigParser


class config:

	nzbmatrix_apikey = '14e8cda5ee64ea984dc5ec2da44a8e83'
	thetvdb_apikey = 'DFDB0A667C844513'
	rt_apikey = 'caxewwhecy767pye7zr3dfrb'
	use_cache = True

	config_filename = 'nzb_config.ini'
	user_config = os.path.join (
		os.environ ['HOME'],	# '/Users/sm/'
		'.nzb',
		config_filename
	)
	#realpath = os.path.realpath (sys.argv[0])
	#dirname = os.path.dirname (realpath)
	#app_config = os.path.join (dirname, config_filename)

	user_config_exists = app_config_exists = True
	if not os.path.exists (user_config):
		user_config_exists = False
	#if not os.path.exists (app_config):
	#	app_config_exists = False
	if (not user_config_exists) and (not app_config_exists):
		print 'Both config files do not exist.  At lease one must exist'
		print '%s and %s are missing' % (user_config, app_config)
		exit()

	cfg = ConfigParser.ConfigParser()
	# only use user config, not app config
	# cfg.read ([user_config, app_config])
	cfg.read ([user_config])

	try:
		# [App Settings]
		tv_max_size = cfg.get ('App Settings', 'tv max size')
		movie_max_size = cfg.get ('App Settings', 'movie max size')
		# [File Locations]
		db_file = os.path.expanduser (cfg.get ('File Locations', 'db file'))
		staging = os.path.expanduser (cfg.get ('File Locations', 'staging'))

	except ConfigParser.NoOptionError as err_msg:
		print err_msg

if __name__ == '__main__':
	pass
