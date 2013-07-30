#!/usr/bin/python

import string
import random
import ctypes
import threading
import sys, os
import time
import unicodedata


class U:

	"""Utility class containing usefull stuff"""

	__esc = "[%im"

	__blackf	= __esc % 30
	__bluef		= __esc % 34
	__cyanf		= __esc % 36
	__greenf	= __esc % 32
	__purplef	= __esc % 35
	__redf		= __esc % 31
	__whitef	= __esc % 37
	__yellowf	= __esc % 33

	__blackb	= __esc % 40
	__blueb		= __esc % 44
	__cyanb		= __esc % 46
	__greenb	= __esc % 42
	__purpleb	= __esc % 45
	__redb		= __esc % 41
	__whiteb	= __esc % 47
	__yellowb	= __esc % 43

	__boldon	= __esc % 1
	__boldoff	= __esc % 22
	__italicon  = __esc % 3
	__italicoff = __esc % 23
	__ulon		= __esc % 4
	__uloff		= __esc % 24
	__invon		= __esc % 7
	__invoff	= __esc % 27

	__reset		= __esc % 0


	@staticmethod
	def fg_color (color, str):

		if color == "black":
			str = U.__blackf + str
		if color == "blue":
			str = U.__bluef + str
		if color == "green":
			str = U.__greenf + str
		if color == "yellow":
			str = U.__yellowf + str
		if color == "purple":
			str = U.__purplef + str
		if color == "red":
			str = U.__redf + str
		if color == 'cyan':
			str = U.__cyanf + str
		if color == 'white':
			str = U.__whitef + str

		return str + U.__reset

	@staticmethod
	def effects (effects, str):
		fmt_str = []
		for effect in effects:
			# if effect == 'boldon':
				# fmt_str += U.__boldon
			# if effect == 'ulon':
				# fmt_str += U.__ulon
			# if effect == 'yellowf':
				# fmt_str += U.__yellowf

			if effect == 'blackf':
				fmt_str.append (U.__blackf)
			if effect == 'bluef':
				fmt_str.append (U.__bluef)
			if effect == 'cyanf':
				fmt_str.append (U.__cyanf)
			if effect == 'greenf':
				fmt_str.append (U.__greenf)
			if effect == 'purplef':
				fmt_str.append (U.__purplef)
			if effect == 'redf':
				fmt_str.append (U.__redf)
			if effect == 'whitef':
			 	fmt_str.append (U.__whitef)
			if effect == 'yellowf':
			 	fmt_str.append (U.__yellowf)
			if effect == 'blackb':
			 	fmt_str.append (U.__blackb)
			if effect == 'blueb':
			 	fmt_str.append (U.__blueb)
			if effect == 'cyanb':
			 	fmt_str.append (U.__cyanb)
			if effect == 'greenb':
			 	fmt_str.append (U.__greenb)
			if effect == 'purpleb':
			 	fmt_str.append (U.__purpleb)
			if effect == 'redb':
			 	fmt_str.append (U.__redb)
			if effect == 'whiteb':
			 	fmt_str.append (U.__whiteb)
			if effect == 'yellowb':
			 	fmt_str.append (U.__yellowb)
			if effect == 'boldon':
			 	fmt_str.append (U.__boldon)
			if effect == 'boldoff':
			 	fmt_str.append (U.__boldoff)
			if effect == 'italicon':
			 	fmt_str.append (U.__italicon)
			if effect == 'italicoff':
			 	fmt_str.append (U.__italicoff)
			if effect == 'ulon':
			 	fmt_str.append (U.__ulon)
			if effect == 'uloff':
			 	fmt_str.append (U.__uloff)
			if effect == 'invon':
			 	fmt_str.append (U.__invon)
			if effect == 'invoff':
			 	fmt_str.append (U.__invoff)

		return ''.join (fmt_str) + str + U.__reset

	@staticmethod
	def hi_color (str, foreground=None, background=None):
		# accept a range from 16 to 231
		if foreground and (foreground < 16 or foreground > 231):
			U.error ('number less than 16 or more than 231')
		if background and (background < 16 or background > 2310):
			U.error ('number less than 16 or more than 231')

		foreground_pat = background_pat = ''
		if foreground:
			foreground_pat = '[38;5;%sm' % (foreground)
		if background:
			background_pat = '[48;5;%sm' % (background)
		reset = '[0m'

		# print foreground_pat, type(foreground_pat)
		# print type(background_pat)
		# print '---', str, '---'
		# print (type (reset))

		ret_str = foreground_pat + background_pat + str + reset
		return ret_str


	@staticmethod
	def wr (*msg):

		print U.pretty_format (*msg)

	@staticmethod
	def is_windows_console():

		# Try and determine console type
		try:
			h = ctypes.windll.kernel32.GetStdHandle(-12)
			csbi = ctypes.create_string_buffer(22)
			res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)

			if res:
				is_console = True
				# import struct
				# (bufx, bufy, curx, cury, wattr,
				 # left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
				# sizex = right - left + 1
				# sizey = bottom - top + 1
			else:
				is_console = False
				# sizex, sizey = 80, 25 # can't determine actual size - return default values
		except:
			is_console = False

		return is_console


	@staticmethod
	def pretty_format (*msg):

		if U.is_windows_console():
			sep = ' | '
			dict_sep = ':'
		else:
			sep = U.__redf + '|' + U.__reset
			dict_sep = U.__redf + ':' + U.__reset


		ret_list = []
		for val in msg:
			if type (val) in (str, unicode):
				ret_list.append (val.encode ("utf-8"))

			elif type (val) == int:
				ret_list.append (str (val))

			elif type (val) in (tuple, list):
				for val2 in val:
					ret_list.append (U.pretty_format (val2))

			elif type (val) == dict:
				for val2 in val:
					ret_list.append (
						U.pretty_format (
							val2 + dict_sep + str (val[val2])))

			else:
				ret_list.append (val)
				# print U.error (type (val))

		return (sep.join(ret_list))

	@staticmethod
	def error (msg="No error message"):
		if U.is_windows_console():
			print "UTIL ERROR:", msg
		else:
			print U.__redb + "UTIL ERROR:" + U.__reset, msg
		exit()

	@staticmethod
	def stop (msg="[Program halted]"):
		if U.is_windows_console():
			print msg
		else:
			print U.__greenb + msg + U.__reset
		exit()

	@staticmethod
	def snip (text, length):
		sep = '+'
		if len (text) <= length:
			return text

		sep_len = len (sep)
		if U.is_odd (length):
			end_half = 0
		else:
			end_half = 1

		middle = len(text) / 2
		short_mid = length / 2
		start = text [0 : short_mid]
		end = text [short_mid + end_half - short_mid * 2 : len (text)]

		if U.is_windows_console():
			color_sep = sep
		else:
			color_sep = U.__greenf + U.__boldon + sep + U.__reset

		return start + color_sep + end

	@staticmethod
	def is_odd (val):
		return val % 2 and True or False

	@staticmethod
	def randomize_sequence (l):
		length = len(l)
		for i in range(length):
			j = random.randrange(i, length)
			l[i], l[j] = l[j], l[i]

	@staticmethod
	def pretty_filesize (bytes):
		bytes = float(bytes)
		if bytes >= 1099511627776:
			terabytes = bytes / 1099511627776
			size = '%.2f TB' % terabytes
		elif bytes >= 1073741824:
			gigabytes = bytes / 1073741824
			size = '%.2f GB' % gigabytes
		elif bytes >= 1048576:
			megabytes = bytes / 1048576
			size = '%.2f MB' % megabytes
		elif bytes >= 1024:
			kilobytes = bytes / 1024
			size = '%.2f KB' % kilobytes
		else:
			size = '%.2f b' % bytes
		return size


class SpinCursor (threading.Thread):

	'''
	A console spin cursor class
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/534142

	Use the SpinCursor class to indicate that your program is busy
	doing something. The cursor can be customized to set its min spin
	count, max spin count and number of spins per second.

	Example Usage...

	# This will spin 5 times even if the data arrives early...
	spin = SpinCursor (minspin=5, msg="Waiting for data...")
	spin.start()

	if data_arrived():
	spin.join()

	# This will spin only during the waiting time...
	spin = SpinCursor (msg="Waiting for data...")
	spin.start()

	if data_arrived():
	spin.stop()

	# This will spin really fast...!
	spin = SpinCursor (msg="I am really busy...", speed=50)
	spin.start()

	'''


	def __init__ (self, msg='', maxspin=0, minspin=10, speed=5):

		# Count of a spin
		self.count = 0
		self.out = sys.stdout
		self.flag = False
		self.max = maxspin
		self.min = minspin
		# Any message to print first ?
		self.msg = msg
		# Complete printed string
		self.string = ''
		# Speed is given as number of spins a second
		# Use it to calculate spin wait time
		self.waittime = 1.0 / float (speed * 4)
		if os.name == 'posix':
			self.spinchars = (unicodedata.lookup ('FIGURE DASH'), u'\\ ', u'| ', u'/ ')
			self.spinchars = (u'-', u'\\ ', u'| ', u'/ ')
		else:
			# The unicode dash character does not show
			# up properly in Windows console.
			self.spinchars = (u'-', u'\\ ', u'| ', u'/ ')

		threading.Thread.__init__ (self, None, None, "Spin Thread")

	def spin (self):

		""" Perform a single spin """

		for x in self.spinchars:
			self.string = self.msg + " " + x + "\r"
			self.out.write (self.string.encode ('utf-8'))
			self.out.flush()
			time.sleep (self.waittime)

	def run (self):

		while (not self.flag) and ((self.count < self.min) or (self.count < self.max)):
			self.spin()
			self.count += 1

		# Clean up display...
		self.out.write (" " * (len (self.string) + 1))

	def stop (self):

		self.flag = True


if __name__ == '__main__':

	line = "-" * 50
        #
	#print "\nTesting U.is_windows_console\n", line
        #
	#print "Is windows console?", U.is_windows_console()
        #
        #
	#print "\nTesting U.wr\n", line
        #
	#U.wr ("single string")
	#U.wr ("two strings", "another")
	#U.wr ("a bunch", "a", "b", "c", "d", "e")
	#U.wr ("numbers:", 100, 200, 300)
	#U.wr (("tuple", "tuple 2"))
	#U.wr (["list", "list 2"])
	#U.wr ({"key 1": "key 1 value", "key 2": "key 2 value"})
	#U.wr ("A complex one", ("Nested", ("one", 2, 3)), [1, 2, {"dict1":"dict1_val", "dict2":"dict2_val"}, 3])


	print "\nTesting U.snip -- U.snip (<text>, <length>)\n", line

	seq = "abcdefghijklmnopqrstuvwxyz"
	length = 13
	for i in range (30):
		U.wr (U.snip (seq[0:i], length).ljust (length), "<")

        for i in range(20,30):

            print U.snip(seq, i)


	#print "\nTesting U.randomize_sequence -- U.randomize_sequence (<seq>)\n", line
        #
	#seq = range (10)
	#print seq, '\n'
	#for x in range (5):
	#        U.randomize_sequence (seq)
	#        print seq
        #
        #
	#print '\nTesting U.hi_color() -- U.hi_color (<text>, <foreground>, <background>)\n', line
        #
	#k = int (15)
	#for i in range (17, 52):
	#        pad = ''
	#        for j in range (6):
	#        	k += 1
	#        	if   len (str (k)) == 1: pad = '   '
	#        	elif len (str (k)) == 2: pad = '  '
	#        	elif len (str (k)) == 3: pad = ' '
        #
	#        	label = ' ' + str (k) + pad
	#        	print U.hi_color (label, foreground=16, background=k),
	#        print ''
        #
        #
	#print '\nTest effects -- U.effects (<[effect list]>, <text>)\n', line
        #
	#effects = ['blackf', 'bluef', 'cyanf', 'greenf', 'purplef', 'redf',
	#        	   'whitef', 'yellowf', 'blackb', 'blueb', 'cyanb', 'greenb',
	#        	   'purpleb', 'redb', 'whiteb', 'yellowb', 'boldon',
	#        	   'italicon', 'ulon']
        #
	#for eff in effects:
	#        print U.effects ([eff], eff)
        #
	#print ''
	#print 'Combining effects:'
	#for e in range (10):
	#        U.randomize_sequence (effects)
	#        print U.effects ([effects[0], effects[1], effects[2]],
	#        				 '%s %s %s' % (effects[0], effects[1], effects[2]))
        #
        #
        #
	#print ''
	#print U.effects (['boldon', 'ulon', 'greenf'],
	#        			 'This text should have bold, underline, and green text')







	## print '\nTest SpinCursor\n', line
	##
	## # spin = SpinCursor (msg="Spinning...", minspin=5, speed=5)
	## # spin.start()
	##
	## spin = SpinCursor (msg="Spinning another time", minspin=10, speed=2)
	## spin.start()
